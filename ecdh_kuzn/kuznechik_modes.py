from myutils import strxor

def pad_size(data_size, blocksize):
    if data_size < blocksize:
        return blocksize - data_size
    if data_size % blocksize == 0:
        return 0
    return blocksize - data_size % blocksize


def pad2(data, blocksize):
    return data + b"\x80" + b"\x00" * pad_size(len(data) + 1, blocksize)


def unpad2(data, blocksize):
    last_block = bytearray(data[-blocksize:])
    pad_index = last_block.rfind(b"\x80")
    if pad_index == -1:
        raise ValueError("Invalid padding")
    for c in last_block[pad_index + 1:]:
        if c != 0:
            raise ValueError("Invalid padding")
    return data[:-(blocksize - pad_index)]

def ecb_encrypt(encrypter, bs, pt):
    if not pt or len(pt) % bs != 0:
        raise ValueError("Plaintext is not blocksize aligned")
    ct = []
    for i in xrange(0, len(pt), bs):
        ct.append(encrypter(pt[i:i + bs]))
    return b"".join(ct)


def ecb_decrypt(decrypter, bs, ct):
    if not ct or len(ct) % bs != 0:
        raise ValueError("Ciphertext is not blocksize aligned")
    pt = []
    for i in xrange(0, len(ct), bs):
        pt.append(decrypter(ct[i:i + bs]))
    return b"".join(pt)