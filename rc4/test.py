from rc4 import RC4

key = [1]*100
cipher = RC4(key)
msg = list(map(ord, b'somecoolmessage'))
enc = msg[:]
for i in range(len(msg)):
    enc[i] ^= cipher.keystream()

cipher.init_state()
dec = enc[:]
for i in range(len(enc)):
    dec[i] ^= cipher.keystream()
    
assert dec == msg
