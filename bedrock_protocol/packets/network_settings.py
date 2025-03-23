import binascii
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo
from bedrock_protocol.packets.bedrock_packet import BedrockPacket

class NetworkSettings(BedrockPacket):
    def __init__(self, server):
        super().__init__()
        self.server = server

        self.compression_threshold = 1
        self.compression_algorithm = 0
        self.enable_client_throttling = False
        self.client_throttle_threshold = 0
        self.client_throttle_scalar = 0.0

    def create_packet(self):
        """Crée un paquet NetworkSettings encodé."""
        self.reset()
        self.write_byte(BedrockProtocolInfo.NETWORK_SETTINGS)
        self.write_short(self.compression_threshold)
        self.write_short(self.compression_algorithm)
        self.write_bool(self.enable_client_throttling)
        self.write_byte(self.client_throttle_threshold)
        self.write_float(self.client_throttle_scalar)

        raw_data = self.get_value()
        self.server.logger.debug(f"📦 Network Settings Raw Data (Final+Fix): {binascii.hexlify(raw_data).decode()}")
        return raw_data
