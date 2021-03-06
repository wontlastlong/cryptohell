import securechat
import ecdhe_agreement
import testcryptor
import socket
import sys
import traceback
from select import select

def on_recv(data):
    print data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((sys.argv[1], int(sys.argv[2])))
s.listen(1)

try:
    client_conn, _ = s.accept()
    chat = securechat.SecureChat(client_conn, 256, None,
        ecdhe_agreement.ECDHEAgreement, testcryptor.TestCryptor, on_recv, True)
    chat.start()

    while chat.running_flag:
        rdy_read, _, _ = select([sys.stdin], [], [], 0.2)
        if rdy_read:
            to_send = raw_input()
            if to_send == ":quit":
                break
            chat.send(to_send)

    chat.close()
except securechat.ChatException:
    print 'meh?'
    sys.stdout.flush()
    chat.close()
    s.close()
    #print str(e)
    traceback.print_exc()