from people.adversary import Adversary
from people.person import Person as Bob


def task():
    shared_base = 666
    shared_prime = 6661

    bob = Bob(shared_base, shared_prime)
    adversary = Adversary(shared_base, shared_prime)


    bobs_private_key = adversary.find_person_private_key(bob.public_key)
    print(bobs_private_key, bob.private_key)


if __name__ == '__main__':
    task()