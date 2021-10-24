import asyncio

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh, rsa, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, \
    load_pem_public_key, ParameterFormat, load_pem_parameters

from assignment2.communicator import Communicator


class Party:
    def __init__(self, name, starting, **kwargs):
        self.name = name
        self.starting = int(starting)

        self.communicator = Communicator(self.starting)
        self.parameters = None
        self.rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                                                        backend=default_backend())
        self.rsa_public_key = self.rsa_private_key.public_key()
        self.other_party_rsa_public_key = None

        self._dh_private_key = None
        self._dh_public_key = None

        self.shared_key = None
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
        await self.rsa_exchange()
        await self.diffie_hellman_exchange()

    async def rsa_exchange(self):
        await self.communicator.send_message(
            self.rsa_public_key.public_bytes(format=PublicFormat.SubjectPublicKeyInfo,
                                             encoding=Encoding.PEM))
        other_party_public_rsa_key = await self.communicator.receive_message()
        self.other_party_rsa_public_key = load_pem_public_key(other_party_public_rsa_key,
                                                              backend=default_backend())

    async def diffie_hellman_exchange(self):
        if self.starting:
            self.parameters = dh.generate_parameters(generator=2, key_size=512,
                                                     backend=default_backend())
            message = self.parameters.parameter_bytes(encoding=Encoding.PEM,
                                                      format=ParameterFormat.PKCS3)
            signature = self._sign_message(message)
            await self.communicator.send_message(message)
            await self.communicator.send_message(signature)
        else:
            message = await self.communicator.receive_message()
            signature = await self.communicator.receive_message()
            self._verify_message(message, signature)
            self.parameters = load_pem_parameters(message, backend=default_backend())

        public_key_bytes = self.dh_public_key.public_bytes(format=PublicFormat.SubjectPublicKeyInfo,
                                                           encoding=Encoding.PEM)
        pkb_signature = self._sign_message(public_key_bytes)
        await self.communicator.send_message(public_key_bytes)
        await self.communicator.send_message(pkb_signature)
        other_party_public_dh_key = await self.communicator.receive_message()
        oppdk_signature = await self.communicator.receive_message()
        self._verify_message(other_party_public_dh_key, oppdk_signature)
        oppk = load_pem_public_key(other_party_public_dh_key, backend=default_backend())
        self.shared_key = self.dh_private_key.exchange(oppk)
        # # TODO: decide if we need that (it is more secure but who knows)
        # derived_key = HKDF(algorithm=hashes.SHA256(),
        #                    length=32,
        #                    salt=None,
        #                    info=b'handshake data',
        #                    backend=default_backend()).derive(self.shared_key)

    def make_throws(self, throws_number):
        pass

    def _sign_message(self, message):
        signature = self.rsa_private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return signature

    def _verify_message(self, message, message_signature):
        self.other_party_rsa_public_key.verify(
            message_signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())

    def __repr__(self):
        return f"name: {self.name}, starting: {self.starting}"
