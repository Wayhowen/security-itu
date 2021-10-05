from people.adversary import Adversary
from people.person import Person as Alice
from people.person import Person as Bob


def task():
    shared_base = 666
    shared_prime = 6661
    message = 2000

    alice = Alice(shared_base, shared_prime)
    print(f"Alice has private key: {alice.private_key}, public key: {alice.public_key}")
    bob = Bob(shared_base, shared_prime)
    print(f"Bob has private key: {bob.private_key}, public key: {bob.public_key}")
    adversary = Adversary(shared_base, shared_prime)

    encrypted_message = alice.encrypt_message(message, bob.public_key)
    print(f"Encrypted message is: {encrypted_message}")
    encrypted_message = adversary.modify_message_contents(encrypted_message)
    print(f"Encrypted message modified by adversary is: {encrypted_message}")
    decrypted_message = bob.decrypt_message(encrypted_message, alice.public_key)
    print(f"Decrypted modified message is: {decrypted_message}")


if __name__ == '__main__':
    task()
