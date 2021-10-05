from people.adversary import Adversary
from people.person import Person as Bob
from people.person import Person as Alice


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
    bobs_private_key = adversary.find_person_private_key(bob.public_key)
    print(f"Adversary found bobs private key to be: {bobs_private_key}")
    decrypted_message = adversary.decrypt_message(encrypted_message, bobs_private_key,
                                                  alice.public_key)
    print(f"Decrypted message is: {decrypted_message}")


if __name__ == '__main__':
    task()
