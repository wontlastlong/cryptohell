class TestCryptor:
    def __init__(self):
        self.rc4 = None

    def set_key(self, key):
        self.rc4 = RC4(list(map(ord, key)))

    def encrypt(self, data):
        list_data = list(map(ord, data))
        list_data = [self.rc4.keystream() ^ x for x in list_data]

        enc_data = ''.join(map(chr, list_data))
        return enc_data

    def decrypt(self, enc_data):
        return self.encrypt(enc_data)

class RC4:
    def __init__(self, key):
        self.key = key
        self.init_state()
    
    def init_state(self):
        n = len(self.key)
        state = [i for i in range(256)]
        j = 0
        for i in range(256):
            j = (j + state[i] + self.key[i % n]) % 256
            state[i], state[j] = state[j], state[i]
        self.state = state
        self.i = 0
        self.j = 0
    
    # NEED MOAR SELFS
    def keystream(self):
        self.i = (self.i + 1) % 256
        self.j = (self.j + self.state[self.i]) % 256
        self.state[self.i], self.state[self.j] = self.state[self.j], self.state[self.i]

        return self.state[(self.state[self.i] + self.state[self.j]) % 256]