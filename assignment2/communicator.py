import asyncio
import sys

import websockets


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

    async def send_message(self, message):
        await self._to_send.put(message)
        while self._to_send.full():
            await asyncio.sleep(0.1)

    async def receive_message(self, ):
        return await self._received.get()
