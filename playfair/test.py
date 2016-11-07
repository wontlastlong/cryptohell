from playfair import PlayFair

cipher = PlayFair('TESTKEY','Q','I')
s = 'TESTMESSAGEQQQ'
assert cipher.decrypt(cipher.encrypt(s)) == 'TESTMESSAGEIII'