from copy import deepcopy


def xgcd(a, b):
    sp, sn = 1, 0
    tp, tn = 0, 1
    
    while b != 0:
        q = a//b
        sp, sn = sn, sp - q*sn
        tp, tn = tn, tp - q*tn
        a, b = b, a - q*b
        
    return a, sp, tp


def inverse(a, mod):
    g, x, _ = xgcd(a, mod)
    if g != 1:
        return None
    return x


def det(m, mod):
    a = deepcopy(m)
    div = 1
    n = len(m)
    b = [[0 for i in range(n)] for i in range(n)]
    
    for k in range(n - 1):
        for i in range(n):
            for j in range(n):
                b[i][j] = (a[k][k]*a[i][j] - a[k][j]*a[i][k])//div
        div = a[k][k]
        if div == 0:
            return 0
        a = deepcopy(b)
        
    return a[n - 1][n - 1] % mod


# stupid way
def inverse_matrix(m, d, mod):
    n = len(m)
    d = inverse(d, mod)
    a = [[0 for i in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            t = [[m[x][y] for x in range(n) if x != i] for y in range(n) if y != j]
            sign = 1 if (i + j) % 2 == 0 else (mod - 1)
            a[j][i] = (d*det(t, mod)*sign) % mod
    return a
    
    
def mult(row, m, mod):
    n = len(row)
    t = [0 for i in range(n)]
    for i in range(n):
        for j in range(n):
            t[i] += row[j]*m[j][i]
        t[i] %= mod
    return t
    

class Hill:
    def __init__(self, key, mod=26):
        n = len(key)
        for i in range(n):
            if len(key[i]) != n:
                raise ValueError('Key matrix is of wrong form! Should be NxN')
        
        d = det(key, mod)
        if d == 0 or xgcd(d, mod)[0] != 1:
            raise ValueError('Key matrix is not invertible!')
        
        self.mod = mod
        self.block_size = n
        self.key_enc = key
        self.key_dec = inverse_matrix(key, d, mod)
    
    def encrypt(self, s):
        t = s[:]
        x = self.block_size - len(t) % self.block_size
        t += [x]*x
        n = len(t)
        
        enc = []
        for i in range(0, n, self.block_size):
            enc += mult(t[i:i+self.block_size], self.key_enc, self.mod)
        return enc
    
    def decrypt(self, s):
        t = s[:]
        n = len(t)
        if n % self.block_size != 0:
            raise ValueError('Data length doesn\'t match block size!')
        
        dec = []
        for i in range(0, n, self.block_size):
            dec += mult(t[i:i+self.block_size], self.key_dec, self.mod)
         
        return dec[:-dec[-1]]