import re

ALPH = [chr(ord('A') + i) for i in range(26)]
upper = re.compile('[A-Z]')

class PlayFair:
    def __init__(self, key, map_from='J', map_to='I'):
        if not (upper.match(key) and upper.match(map_from) and upper.match(map_to)):
            raise ValueError('Uppercase letters only!')
        if map_to == map_from:
            raise ValueError('Wrong mapping! %s -> %s' % (map_from, map_to))
        
        self.map_from = map_from
        self.map_to = map_to
        self.set_key(key)
        
    def set_key(self, key):
        m = [['*' for i in range(5)] for i in range(5)]
        used = {c:False for c in ALPH}
        used[self.map_from] = True
        key = key.replace(self.map_from, self.map_to)
        
        cur = 0
        for c in key:
            if not used[c]:
                m[cur//5][cur%5] = c
                used[c] = True
                cur += 1
        
        for v in used.items():
            if not v[1]:
                m[cur//5][cur%5] = v[0]
                cur += 1
        
        assert cur == 25
        
        mapping_enc = {}
        for i in range(5):
            for j in range(5):
                for x in range(5):
                    for y in range(5):
                        from_ = m[i][j] + m[x][y]
                        if (i, j) == (x, y):
                            to_ = m[(i + 1) % 5][(j + 1) % 5] + m[(x + 1) % 5][(y + 1) % 5] 
                        elif i == x:
                            to_ = m[i][(j + 1) % 5] + m[x][(y + 1) % 5]
                        elif j == y:
                            to_ = m[(i + 1) % 5][j] + m[(x + 1) % 5][y]
                        else:
                            to_ = m[i][y] + m[x][j]
                        
                        mapping_enc[from_] = to_
        
        self.key_enc = mapping_enc
        self.key_dec = {t:f for f, t in mapping_enc.iteritems()}
        
        
    def encrypt(self, s):
        if not upper.match(s):
            raise ValueError('Uppercase letters only!')
        s = s.replace(self.map_from, self.map_to)
        
        enc = ''
        for i in range(0, len(s), 2):
            block = s[i:i+2]
            if len(block) == 1:
                block += 'X'
            enc += self.key_enc[block]
        
        return enc
    
    def decrypt(self, s):
        if not upper.match(s):
            raise ValueError('Uppercase letters only!')
        if len(s) % 2 != 0:
            raise ValueError('Odd length string')
        
        dec = ''
        for i in range(0, len(s), 2):
            block = s[i:i+2]
            dec += self.key_dec[block]
        
        return dec
            
                            
                
                
        