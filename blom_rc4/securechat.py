import socket
import threading
import json
import base64
import myutils
from select import select
import sys

class ChatException(Exception):
    pass

class SecureChat:
    # not really tho
    def __init__(self, client_conn, key_size, keypair, KeyAgreement, Cryptor, recv_handler, initiator=False):
        self.client_conn = client_conn
        self.mode = initiator
        self.agree = KeyAgreement(client_conn, key_size, keypair, self.mode)
        self.cryptor = Cryptor()
        self.key = None
        self.running_flag = False
        self.recv_handler = recv_handler

    def start(self):
        self.key = self.agree.get_key()
        self.cryptor.set_key(self.key)

        self.running_flag = True
        self.recv_thread = threading.Thread(target=self.recv)
        self.recv_thread.start()

    def close(self):
        print 'ok'
        sys.stdout.flush()
        self.running_flag = False
        self.recv_thread.join()

    def send(self, data):
        enc_data = self.cryptor.encrypt(data)
        b64_data = base64.b64encode(enc_data)
        payload = {'msg':b64_data}
        json_payload = json.dumps(payload)
        self.client_conn.send(json_payload)

    def recv(self):
        try:
            while self.running_flag:
                rdy_read, _, _ = select([self.client_conn], [], [], 2)
                if rdy_read:
                    json_payload = myutils.recvall(self.client_conn)
                    payload = json.loads(json_payload)
                    if 'msg' not in payload:
                        continue

                    enc_data = base64.b64decode(payload['msg'])
                    data = self.cryptor.decrypt(enc_data)
                    self.recv_handler(data)
        except Exception as e:
            self.running_flag = False
            raise ChatException(str(e))
