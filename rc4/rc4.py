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

