import json
import base64
from Crypto.Util.number import long_to_bytes, bytes_to_long
import ecc
import myutils

class ECDHEAgreement:
    def __init__(self, conn, key_size, keypair, mode):
        self.conn = conn
        self.key_size = key_size
        self.key_size_bytes = (key_size - 1) / 8 + 1
        self.mode = mode

    def get_key(self):
        if self.mode:
            shared_key = self.init_exchange()
        else:
            shared_key = self.wait_exchange()

        shared_key &= ((1<<self.key_size) - 1)
        shared_key = long_to_bytes(shared_key)
        
        #bts_shared_key = long_to_bytes(shared_key)
        print repr(shared_key)
        return shared_key


    def init_exchange(self):
        self.my_prv_key, my_pub_key = ecc.make_keypair()

        my_keydata = json.dumps( {
            'x' : base64.b64encode(long_to_bytes(my_pub_key[0])),
            'y':base64.b64encode(long_to_bytes(my_pub_key[1]))
        } )


        self.conn.send(my_keydata)

        answer = myutils.recvall(self.conn)
        answer = json.loads(answer)
        if 'x' not in answer or 'y' not in answer:
            raise KeyError('init_exchange(): no "x" or "y" in json data')

        its_keydata = (
            bytes_to_long(base64.b64decode(answer['x'])),
            bytes_to_long(base64.b64decode(answer['y']))
        )

        return self.compute_shared_key(its_keydata)

    def wait_exchange(self):
        answer = myutils.recvall(self.conn)
        answer = json.loads(answer)
        if 'x' not in answer or 'y' not in answer:
            raise KeyError('init_exchange(): no "x" or "y" in json data')

        its_keydata = (
            bytes_to_long(base64.b64decode(answer['x'])),
            bytes_to_long(base64.b64decode(answer['y']))
        )

        self.my_prv_key, my_pub_key = ecc.make_keypair()

        my_keydata = json.dumps( {
            'x' : base64.b64encode(long_to_bytes(my_pub_key[0])),
            'y':base64.b64encode(long_to_bytes(my_pub_key[1]))
        } )
        self.conn.send(my_keydata)

        return self.compute_shared_key(its_keydata)

    def compute_shared_key(self, its_pub_key):
        shared_key = ecc.scalar_mult(self.my_prv_key, its_pub_key)

        return shared_key[0]
