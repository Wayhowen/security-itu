class Adversary:
    def __init__(self, shared_base, shared_prime):
        self._shared_base = shared_base
        self._shared_prime = shared_prime


    def find_person_private_key(self, person_public_key):
        for possible_key in range(1, self._shared_prime - 1):
            bob_public_key = pow(self._shared_base, possible_key, self._shared_prime)
            if bob_public_key == person_public_key:
                return possible_key

    def decrypt_message(self, message, receiver_private_key, sender_public_key):
        cipher = pow(sender_public_key, receiver_private_key, self._shared_prime)
        return message // cipher

    def modify_message_contents(self, encrypted_message):
        return encrypted_message * 3
