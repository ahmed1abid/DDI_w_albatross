from typing import Any
import rsa

class User:
    def __init__(self, name=None, ssn=None, keypair=None, data=None):
        self.name = name
        self.ssn = ssn
        self.data = data
        if keypair is None:
            self.keypair = rsa.newkeys(1024)
        else:
            self.keypair = keypair

    def set_data(self, data):
        self.data = data

    def encrypt_data(self):
        if self.data is not None:
            encrypted_data = rsa.encrypt(self.data.encode('utf-8'), self.keypair[0])
            return encrypted_data
        else:
            return None



		