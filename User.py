from typing import Any
import rsa

class User:
    def __init__(self, name=None, ssn=None, keypair=None, data=None):
        """
        Initialize a User object.

        Args:
            name (str): The name of the user.
            ssn (str): The social security number (SSN) of the user.
            keypair (tuple): A tuple containing the public and private keys generated using RSA.
            data (str): The data associated with the user.

        Attributes:
            name (str): The name of the user.
            ssn (str): The social security number (SSN) of the user.
            data (str): The data associated with the user.
            keypair (tuple): A tuple containing the public and private keys generated using RSA.
        """
        self.name = name
        self.ssn = ssn
        self.data = data
        if keypair is None:
            self.keypair = rsa.newkeys(1024)
        else:
            self.keypair = keypair

    def set_data(self, data):
        """
        Set the data associated with the user.

        Args:
            data (str): The data to be associated with the user.
        """
        self.data = data

    def encrypt_data(self):
        """
        Encrypt the user's data using RSA encryption.

        Returns:
            bytes: The encrypted data.
        """
        if self.data is not None:
            encrypted_data = rsa.encrypt(self.data.encode('utf-8'), self.keypair[0])
            return encrypted_data
        else:
            return None
