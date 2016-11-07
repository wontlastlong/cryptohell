# Hill cipher! Works with any key matrix size, any modulus

from hill import *

# wiki expamples
# key = 'GYBNQKURP'
# msg = 'ACT'
key = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
msg = [0, 2, 19]

cipher = Hill(key, mod=26)
enc = cipher.encrypt(msg)
print(enc)
dec = cipher.decrypt(enc)
print(dec)

key = [[3, 3], [2, 5]]
msg = [7, 4, 11, 15]
cipher = Hill(key, mod=257)
enc = cipher.encrypt(msg)
print(enc)
dec = cipher.decrypt(enc)
print(dec)