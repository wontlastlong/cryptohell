from myutils import strxor

LC = bytearray((
    148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1,
))

PI = bytearray((
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79, 5,
    132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31, 235,
    52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204, 181,
    112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135, 21, 161,
    150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177, 50, 117,
    25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87, 223, 245,
    36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3, 224, 15,
    236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74, 167, 151,
    96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65, 173, 69, 70,
    146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59, 7, 88, 179, 64,
    134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137, 225, 27, 131, 73,
    76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97, 32, 113, 103, 164,
    45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82, 89, 166, 116, 210, 230,
    244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182,
))

PIinv = bytearray(256)
for x in xrange(256):
    PIinv[PI[x]] = x


def gf(a, b):
    c = 0
    while b:
        if b & 1:
            c ^= a
        if a & 0x80:
            a = (a << 1) ^ 0x1C3
        else:
            a <<= 1
        b >>= 1
    return c

GF = [bytearray(256) for _ in xrange(256)]

for x in xrange(256):
    for y in xrange(256):
        GF[x][y] = gf(x, y)


def L(blk, rounds=16):
    for _ in range(rounds):
        t = blk[15]
        for i in range(14, -1, -1):
            blk[i + 1] = blk[i]
            t ^= GF[blk[i]][LC[i]]
        blk[0] = t
    return blk


def Linv(blk):
    for _ in range(16):
        t = blk[0]
        for i in range(15):
            blk[i] = blk[i + 1]
            t ^= GF[blk[i]][LC[i]]
        blk[15] = t
    return blk

C = []

for x in range(1, 33):
    y = bytearray(16)
    y[15] = x
    C.append(L(y))


def lp(blk):
    return L([PI[v] for v in blk])


class Kuznechik(object):
    def __init__(self, key):
        kr0 = bytearray(key[:16])
        kr1 = bytearray(key[16:])
        self.ks = [kr0, kr1]
        for i in range(4):
            for j in range(8):
                k = lp(bytearray(strxor(C[8 * i + j], kr0)))
                kr0, kr1 = [strxor(k, kr1), kr0]
            self.ks.append(kr0)
            self.ks.append(kr1)

    def encrypt(self, blk):
        blk = bytearray(blk)
        for i in range(9):
            blk = lp(bytearray(strxor(self.ks[i], blk)))
        return bytes(strxor(self.ks[9], blk))

    def decrypt(self, blk):
        blk = bytearray(blk)
        for i in range(9, 0, -1):
            blk = [PIinv[v] for v in Linv(bytearray(strxor(self.ks[i], blk)))]
        return bytes(strxor(self.ks[0], blk))