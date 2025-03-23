class FrameSetPacket:
    def __init__(self, raknet):
        self.raknet = raknet
        self.sequence_number = 0
        self.frames = []

    def create_frame(self, data, flags=0x60):
        self.frames.append((flags, data))

    def set_sequence_number(self, sequence_number):
        self.sequence_number = sequence_number

    def encode(self):
        result = struct.pack("<I", self.sequence_number)
        for flags, data in self.frames:
            result += struct.pack("<B", flags) + data
        return result
