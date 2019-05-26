import asyncio
import struct

class ClientError(Exception):
    pass

class InvalidPassword(Exception):
    pass

class MinecraftClient:

    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

        self._auth = None
        self._reader = None
        self._writer = None

    async def __aenter__(self):
        if not self._writer:
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
            await self._authenticate()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._writer:
            self._writer.close()

    async def _authenticate(self):
        if not self._auth:
            await self._send(3, self.password)
            self._auth = True

    async def _read_data(self, leng):
        data = b''
        while len(data) < leng:
            data += await self._reader.read(leng - len(data))

        return data

    async def _send(self, typen, message):
        if not self._writer:
            raise ClientError('Not connected.')

        out = struct.pack('<li', 0, typen) + message.encode('utf8') + b'\x00\x00'
        out_len = struct.pack('<i', len(out))
        self._writer.write(out_len + out)

        in_len = struct.unpack('<i', await self._read_data(4))
        in_payload = await self._read_data(in_len[0])

        in_id, in_type = struct.unpack('<ii', in_payload[:8])
        in_data, in_padd = in_payload[8:-2], in_payload[-2:]

        if in_padd != b'\x00\x00':
            raise ClientError('Incorrect padding.')
        if in_id == -1:
            raise InvalidPassword('Incorrect password.')

        data = in_data.decode('utf8')
        return data

    async def send(self, cmd):
        result = await self._send(2, cmd)
        await asyncio.sleep(0.003) #unsure about this
        return result
