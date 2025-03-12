import zlib

class CompressionManager:
    def __init__(self, server):
        self.server = server

    def compress(self, data):
        return zlib.compress(data)

    def decompress(self, compressed_data):
        try:
            return zlib.decompress(compressed_data)
        except zlib.error as e:
            self.server.logger.error(f"Failed to decompress packet: {e}")
            return None
