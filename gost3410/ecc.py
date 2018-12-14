import collections
import random
from Crypto.Util.number import bytes_to_long, long_to_bytes, getRandomRange

def inverse_mod(k, p):
    if k == 0:
        raise ZeroDivisionError('division by zero')

    if k < 0:
        return p - inverse_mod(-k, p)
        
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = p, k

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    gcd, x, y = old_r, old_s, old_t

    assert gcd == 1
    assert (k * x) % p == 1

    return x % p

class EllipticCurve(object):
    def __init__(self, p, q, a, b):
        self.p = p
        self.q = q
        self.a = a
        self.b = b

    def is_on_curve(self, point):
        if point is None:
            return True

        x, y = point

        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def point_neg(self, point):
        assert self.is_on_curve(point)

        if point is None:
            # -0 = 0
            return None

        x, y = point
        result = (x, -y % self.p)

        assert self.is_on_curve(result)

        return result


    def point_add(self, point1, point2):
        assert self.is_on_curve(point1)
        assert self.is_on_curve(point2)

        if point1 is None:
            return point2
        if point2 is None:
            return point1

        x1, y1 = point1
        x2, y2 = point2

        if x1 == x2 and y1 != y2:
            return None

        if x1 == x2:
            m = (3 * x1 * x1 + self.a) * inverse_mod(2 * y1, self.p)
        else:
            m = (y1 - y2) * inverse_mod(x1 - x2, self.p)

        x3 = m * m - x1 - x2
        y3 = y1 + m * (x3 - x1)
        result = (x3 % self.p,
                  -y3 % self.p)

        assert self.is_on_curve(result)

        return result


    def scalar_mult(self, k, point):
        assert self.is_on_curve(point)

        if k % self.q == 0 or point is None:
            return None

        if k < 0:
            return scalar_mult(-k, point_neg(point))

        result = None
        addend = point

        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)

            k >>= 1

        assert self.is_on_curve(result)

        return result

    def sign(self, point, prv_key, digest, test=False):
        q = self.q
        e = bytes_to_long(digest) % q

        if e == 0:
            e = 1

        while True:
            if test:
                k = 0x77105C9B20BCD3122823C8CF6FCC7B956DE33814E95B7FE64FED924594DCEAB3
            else:
                k = getRandomRange(1, q)

            r, _ = self.scalar_mult(k, point)
            r %= q
            if r == 0:
                continue

            s = (prv_key*r + k*e) % q
            if s == 0:
                continue
            break

        return long_to_bytes(r) + long_to_bytes(s)

    def verify(self, point, pub_key, digest, signature):
        assert len(digest) == 32 or len(digest) == 64
        size = len(digest)

        if len(signature) != size * 2:
            raise ValueError("Invalid signature length")

        q = self.q
        p = self.p
        r = bytes_to_long(signature[:size])
        s = bytes_to_long(signature[size:])

        if r <= 0 or r >= q or s <= 0 or s >= q:
            return False

        e = bytes_to_long(digest) % q
        if e == 0:
            e = 1

        v = inverse_mod(e, q)
        z1 = s*v % q
        z2 = (-r*v) % q

        p1 = self.scalar_mult(z1, point)
        q1 = self.scalar_mult(z2, pub_key)
        R, _ = self.point_add(p1, q1)
        R %= q

        return R == r