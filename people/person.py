import random


class Person:
    def __init__(self, base, shared_prime):
        self._base = base
        self._shared_prime = shared_prime

        self._private_key = None
        self._public_key = None

    @property
    def private_key(self):
        if not self._private_key:
            self._private_key = random.randint(1, self._shared_prime - 1)
        return self._private_key

    @property
    def public_key(self):
        if not self._public_key:
            self._public_key = pow(self._base, self.private_key, self._shared_prime)
        return self._public_key

    def encrypt_message(self, message, receiver_public_key):
        cipher = pow(receiver_public_key, self.private_key, self._shared_prime)
        return message * cipher

    def decrypt_message(self, message, sender_public_key):
        cipher = pow(sender_public_key, self.private_key, self._shared_prime)
        return message // cipher

