import struct
import io

class BedrockPacket:
    def __init__(self, data: bytes = b''):
        self.buffer = io.BytesIO(data)

    def reset(self):
        self.buffer = io.BytesIO()

    def write_byte(self, value):
        self.buffer.write(struct.pack("<B", value))

    def write_short(self, value):
        self.buffer.write(struct.pack("<H", value))

    def write_bool(self, value):
        self.buffer.write(struct.pack("<?", value))

    def write_float(self, value):
        self.buffer.write(struct.pack("<f", value))

    def get_value(self):
        return self.buffer.getvalue()
