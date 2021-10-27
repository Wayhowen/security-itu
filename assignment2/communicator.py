import asyncio
from typing import Optional

import websockets

from encryption_tool import EncryptionTool
from signature_tool import SignatureTool


class Communicator:
    def __init__(self, starting):
        self.starting = int(starting)

        self.host = 'localhost'
        if self.starting:
            self.port = 56789
            self.connect_port = 56790
        else:
            self.port = 56790
            self.connect_port = 56789

        self._to_send = asyncio.Queue(maxsize=1)
        self._received = asyncio.Queue(maxsize=1)

        self._signature_tool: Optional[SignatureTool] = None
        self._encryption_tool: Optional[EncryptionTool] = None

        asyncio.ensure_future(self._run())
        asyncio.ensure_future(self._send_messages())

    async def _run(self):
        async with websockets.serve(self._receive_messages, self.host, self.port):
            while True:
                await asyncio.sleep(1)

    async def _receive_messages(self, socket, _):
        while True:
            try:
                await self._received.put(await socket.recv())
            except websockets.exceptions.ConnectionClosedError:
                pass

    async def _send_messages(self):
        uri = f'ws://{self.host}:{self.connect_port}'
        while True:
            try:
                async with websockets.connect(uri) as socket:
                    while True:
                        message = await self._to_send.get()
                        await socket.send(message)
            except OSError:
                pass

    def set_signature_tool(self, signature_tool):
        self._signature_tool = signature_tool

    def set_encryption_tool(self, encryption_tool):
        self._encryption_tool = encryption_tool

    async def send_message(self, message):
        await self._to_send.put(message)
        while self._to_send.full():
            await asyncio.sleep(0.1)

    async def receive_message(self, ):
        return await self._received.get()

    async def sign_and_send_message(self, message):
        signature = self._signature_tool.sign_message(message)
        await self.send_message(message)
        await self.send_message(signature)

    async def receive_and_verify_signed_message(self):
        message = await self.receive_message()
        signature = await self.receive_message()
        self._signature_tool.verify_message(message, signature)
        return message

    async def sign_encrypt_and_send_message(self, message):
        signature = self._signature_tool.sign_message(message)
        await self.send_message(self._encryption_tool.pad_and_encrypt_message(message))
        await self.send_message(self._encryption_tool.pad_and_encrypt_message(signature))

    async def receive_decrypt_and_verify_message(self):
        unpadded_message = self._encryption_tool.decrypt_and_unpad_message(
            await self.receive_message())
        unpadded_signature = self._encryption_tool.decrypt_and_unpad_message(
            await self.receive_message())
        self._signature_tool.verify_message(unpadded_message, unpadded_signature)
        return unpadded_message
