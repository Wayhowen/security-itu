from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class SignatureTool:
    def __init__(self, rsa_private_key, other_party_rsa_public_key):
        self._rsa_private_key = rsa_private_key
        self._other_party_rsa_public_key = other_party_rsa_public_key

    def sign_message(self, message):
        signature = self._rsa_private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return signature

    def verify_message(self, message, message_signature):
        self._other_party_rsa_public_key.verify(
            message_signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
