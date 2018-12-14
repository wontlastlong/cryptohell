import kuznechik
import kuznechik_modes

class TestCryptor:
    def __init__(self):
        self.kuzn = None

    def set_key(self, key):
        self.kuzn = kuznechik.Kuznechik(key)

    def encrypt(self, data):
        pad_data = kuznechik_modes.pad2(data, 16)
        enc_data = kuznechik_modes.ecb_encrypt(self.kuzn.encrypt, 16, pad_data)
        return enc_data

    def decrypt(self, enc_data):
        pad_data = kuznechik_modes.ecb_decrypt(self.kuzn.decrypt, 16, enc_data)
        data = kuznechik_modes.unpad2(pad_data, 16)
        return data