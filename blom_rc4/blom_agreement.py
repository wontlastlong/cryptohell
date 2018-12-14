import struct
import numpy as np
import StringIO
import json
import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes
import myutils

class BlomKey:
    key_size = None
    q = None
    lambd_p1 = None
    raw = None

    def __init__(self, key_size, q, lambd_p1, raw):
        self.key_size = key_size
        self.q = q
        self.lambd_p1 = lambd_p1
        self.raw = raw

    @classmethod
    def from_bytes(cls, bts):
        data = StringIO.StringIO(bts)
        key_size = struct.unpack('<H', data.read(2))[0]
        print key_size

        prime_size = struct.unpack('<H', data.read(2))[0]

        q = bytes_to_long(data.read(prime_size))
        lambd_p1 = struct.unpack('<H', data.read(2))[0]

        Vi = np.empty((lambd_p1, 1), dtype='object')
        for i in range(lambd_p1):
            elem_size = struct.unpack('<H', data.read(2))[0]
            elem = bytes_to_long(data.read(elem_size))
            Vi[i,0] = elem

        data.close()

        return cls(key_size, q, lambd_p1, bts, Vi)

    @classmethod
    def from_file(cls, fname):
        bts_b64 = open(fname, 'rb').read()
        bts = base64.b64decode(bts_b64)
        return cls.from_bytes(bts)

class BlomPubKey(BlomKey):
    def __init__(self, key_size, q, lambd_p1, raw, Vi):
        BlomKey.__init__(self, key_size, q, lambd_p1, raw)
        self.Gi = Vi

class BlomPrvKey(BlomKey):
    def __init__(self, key_size, q, lambd_p1, raw, Vi):
        BlomKey.__init__(self, key_size, q, lambd_p1, raw)
        self.Ai = Vi.T

class BlomAgreement:
    def __init__(self, conn, key_size, keypair, mode):
        self.conn = conn
        self.key_size = key_size
        self.pub, self.prv = keypair
        self.mode = mode

    def get_key(self):
        if self.mode:
            shared_key = self.init_exchange()
        else:
            shared_key = self.wait_exchange()

        if self.key_size < self.prv.key_size:
            shared_key &= ((1<<self.key_size) - 1)
        
        bts_shared_key = long_to_bytes(shared_key)
        return bts_shared_key


    def init_exchange(self):
        my_keydata = json.dumps( {'pubkey' : base64.b64encode(self.pub.raw)} )
        self.conn.send(my_keydata)

        answer = myutils.recvall(self.conn)
        answer = json.loads(answer)
        if 'pubkey' not in answer:
            raise KeyError('init_exchange(): no "pubkey" in json data')

        its_keydata = base64.b64decode(answer['pubkey'])

        return self.compute_shared_key(its_keydata)

    def wait_exchange(self):
        answer = myutils.recvall(self.conn)
        answer = json.loads(answer)
        if 'pubkey' not in answer:
            raise KeyError('init_exchange(): no "pubkey" in json data')

        its_keydata = base64.b64decode(answer['pubkey'])

        my_keydata = json.dumps( {'pubkey' : base64.b64encode(self.pub.raw)} )
        self.conn.send(my_keydata)

        return self.compute_shared_key(its_keydata)

    def compute_shared_key(self, its_keydata):
        its_pubkey = BlomPubKey.from_bytes(its_keydata)
        shared_key = (np.dot(its_pubkey.Gi, self.prv.Ai) % self.prv.q)[0,0]
        return shared_key
