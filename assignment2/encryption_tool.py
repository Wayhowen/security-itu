from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class EncryptionTool:
    def __init__(self, derived_key, initialization_vector, padding_size=128):
        self._cipher = Cipher(algorithms.AES(derived_key), modes.CBC(initialization_vector),
                              backend=default_backend())
        print(f"Using {self._cipher.algorithm.name} with {self._cipher.mode.name} to encrypt"
              f" the data")

        self._padding_size = padding_size

    def pad_and_encrypt_message(self, message):
        padded_message = self._add_message_padding(message)
        encryptor = self._cipher.encryptor()
        return encryptor.update(padded_message) + encryptor.finalize()

    def decrypt_and_unpad_message(self, message):
        decryptor = self._cipher.decryptor()
        decrypted_message = decryptor.update(message) + decryptor.finalize()
        return self._remove_message_padding(decrypted_message)

    def _add_message_padding(self, message):
        padder = padding.PKCS7(self._padding_size).padder()
        return padder.update(message) + padder.finalize()

    def _remove_message_padding(self, message):
        unpadder = padding.PKCS7(self._padding_size).unpadder()
        return unpadder.update(message) + unpadder.finalize()
