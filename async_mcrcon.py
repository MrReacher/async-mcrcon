import collections
import struct
import asyncio

Packet = collections.namedtuple('Packet', ('ident', 'kind', 'payload'))

class IncompletePacket(Exception):
    def __init__(self, minimum):
        self.minimum = minimum

class MinecraftClient:

    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

        self.auth = False
        self.reader = None
        self.writer = None

    async def __aenter__(self):
        if not self.writer:
            await self.login()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.writer:
            self.writer.close()
            self.auth = False

    def close(self):
        if self.writer:
            self.writer.close()
            self.auth = False

    async def login(self):
        if not self.auth:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.send_packet(Packet(0, 3, self.password.encode('utf8')))
            self.auth = True

            packet = await self.read_data()
            return packet.ident == 0

    def decode_packet(self, data):
        if len(data) < 14:
            raise IncompletePacket(14)

        length = struct.unpack('<i', data[:4])[0] + 4
        if len(data) < length:
            raise IncompletePacket(length)

        ident, kind = struct.unpack('<ii', data[4:12])
        payload, padding = data[12:length-2], data[length-2:length]
        
        assert padding == b'\x00\x00'
        return Packet(ident, kind, payload), data[length:]

    def encode_packet(self, packet):
        data = struct.pack('<ii', packet.ident, packet.kind) + packet.payload + b'\x00\x00'
        return struct.pack('<i', len(data)) + data

    def send_packet(self, packet):
        self.writer.write(self.encode_packet(packet))

    async def read_data(self):
        data = b''
        while True:
            try:
                output = self.decode_packet(data)[0]
                return output
            except IncompletePacket as exc:
                while len(data) < exc.minimum:
                    output = await self.reader.read(exc.minimum - len(data))
                    data += output

    async def send(self, command):
        cmd = command.encode('utf8')

        self.send_packet(Packet(0, 2, cmd))
        self.send_packet(Packet(1, 0, b''))
        
        response = b''
        while True:
            packet = await self.read_data()
            if packet.ident != 0:
                break
            
            response += packet.payload
        
        return response.decode('utf8')
