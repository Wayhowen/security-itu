import os
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import dh, rsa
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, \
    load_pem_public_key, ParameterFormat, load_pem_parameters

from encryption_tool import EncryptionTool
from signature_tool import SignatureTool
from communicator import Communicator


class Party:
    def __init__(self, starting, number_of_throws, **kwargs):
        self.starting = int(starting)
        self.number_of_throws = int(number_of_throws)

        self.parameters = None

        self._dh_private_key = None
        self._dh_public_key = None

        self.communicator = Communicator(self.starting)

        self.shared_key = None
        self.derived_key = None
        print("initialized")

    @property
    def dh_private_key(self):
        if self._dh_private_key is None:
            self._dh_private_key = self.parameters.generate_private_key()
        return self._dh_private_key

    @property
    def dh_public_key(self):
        if self._dh_public_key is None:
            self._dh_public_key = self.dh_private_key.public_key()
        return self._dh_public_key

    async def work(self):
        # This rsa exchange is insecure, however this is equivalent of assuming, that we know
        # other party public rsa key in advance
        print("=== RSA ===")
        await self.rsa_exchange()
        print("=== DIFFIE-HELLMAN ===")
        await self.diffie_hellman_exchange()
        print("=== GAME OF DICE ===")
        for i in range(1, self.number_of_throws + 1):
            print(f"=== Throw {i} ===")
            await self.make_throw()

    async def rsa_exchange(self):
        # generate private-public keypair
        rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                                                   backend=default_backend())
        rsa_public_key = rsa_private_key.public_key()
        # send public key to other party and receive theirs
        await self.communicator.send_message(
            rsa_public_key.public_bytes(format=PublicFormat.SubjectPublicKeyInfo,
                                        encoding=Encoding.PEM))
        other_party_public_rsa_key = await self.communicator.receive_message()
        other_party_rsa_public_key = load_pem_public_key(other_party_public_rsa_key,
                                                         backend=default_backend())
        # set signature tool to sign our messages and verify other party messages
        signature_tool = SignatureTool(rsa_private_key, other_party_rsa_public_key)
        self.communicator.set_signature_tool(signature_tool)

    async def diffie_hellman_exchange(self):
        if self.starting:
            self.parameters = dh.generate_parameters(generator=2, key_size=512,
                                                     backend=default_backend())
            message = self.parameters.parameter_bytes(encoding=Encoding.PEM,
                                                      format=ParameterFormat.PKCS3)
            await self.communicator.sign_and_send_message(message)
        else:
            message = await self.communicator.receive_and_verify_signed_message()
            self.parameters = load_pem_parameters(message, backend=default_backend())

        public_key_bytes = self.dh_public_key.public_bytes(format=PublicFormat.SubjectPublicKeyInfo,
                                                           encoding=Encoding.PEM)
        await self.communicator.sign_and_send_message(public_key_bytes)
        other_party_public_dh_key = await self.communicator.receive_and_verify_signed_message()
        oppk = load_pem_public_key(other_party_public_dh_key, backend=default_backend())
        self.shared_key = self.dh_private_key.exchange(oppk)
        print(f"Shared key is: {self.shared_key}")
        self.derived_key = HKDF(algorithm=hashes.SHA256(),
                                length=32,  # 256 bits
                                salt=None,
                                info=b'handshake data',
                                backend=default_backend()).derive(self.shared_key)
        print(f"Derived key is: {self.derived_key}")

    async def make_throw(self):
        # initialization vector doesn't have to be encoded
        if self.starting:
            initialization_vector = os.urandom(16)
            await self.communicator.sign_and_send_message(initialization_vector)
        else:
            initialization_vector = await self.communicator.receive_and_verify_signed_message()
        print(f"Initialization vector set to: {initialization_vector}")

        encryption_tool = EncryptionTool(self.derived_key, initialization_vector)
        self.communicator.set_encryption_tool(encryption_tool)

        local_throw = self._make_a_throw()
        print(f"Local throw is: {local_throw}")

        if self.starting:
            random_value = os.urandom(32)

            concatenated_values = local_throw + random_value
            commitment = hashes.Hash(hashes.SHA256(), backend=default_backend())
            commitment.update(concatenated_values)
            commitment = commitment.finalize()

            await self.communicator.sign_encrypt_and_send_message(commitment)
        else:
            await self.communicator.sign_encrypt_and_send_message(local_throw)

        received_message = await self.communicator.receive_decrypt_and_verify_message()

        if self.starting:
            await self.communicator.sign_encrypt_and_send_message(local_throw)
            await self.communicator.sign_encrypt_and_send_message(random_value)
            other_client_throw = received_message
        else:
            other_client_throw = await self.communicator.receive_decrypt_and_verify_message()
            other_client_random_value = await self.communicator.receive_decrypt_and_verify_message()

            concatenated_values = other_client_throw + other_client_random_value
            rec_digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            rec_digest.update(concatenated_values)
            digest_bytes = rec_digest.finalize()
            if digest_bytes != received_message:
                raise Exception("Other client changed their commitment")

        print("Received throw", other_client_throw)
        throw_result = (int(local_throw.decode()) + int(other_client_throw.decode())) % 6 + 1
        print(f"The resulting throw is: {throw_result}")
        self.starting = int(not self.starting)

    def _make_a_throw(self):
        # TODO: change it to uniform function
        our_throw = int.from_bytes(os.urandom(16), sys.byteorder) % 6 + 1
        return f"{our_throw}".encode()

    def _add_message_padding(self, message, padding_size=128):
        padder = padding.PKCS7(padding_size).padder()
        return padder.update(message) + padder.finalize()

    def __repr__(self):
        return f"name: {self.name}, starting: {self.starting}"
