from people.person import Person as Alice
from people.person import Person as Bob


def task():
    shared_base = 666
    shared_prime = 6661
    message = 2000

    alice = Alice(shared_base, shared_prime)
    bob = Bob(shared_base, shared_prime)

    encrypted_message = alice.encrypt_message(message, bob.public_key)
    decrypted_message = bob.decrypt_message(encrypted_message, alice.public_key)

    print(decrypted_message)

if __name__ == '__main__':
    task()