import struct
import binascii
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class NetworkSettings:
    def __init__(self, server):
        self.server = server

        self.compression_threshold = 256
        self.compression_algorithm = 1
        self.enable_client_throttling = True
        self.client_throttle_threshold = 10
        self.client_throttle_scalar = 1.0

    def handle_request(self, connection):
        self.server.logger.info(f"📡 Received Request Network Settings from {connection.address}")
    
        packet = struct.pack("<B", BedrockProtocolInfo.NETWORK_SETTINGS)
        packet += struct.pack("<H", self.compression_threshold)
        packet += struct.pack("<H", self.compression_algorithm)
        packet += struct.pack("<?", self.enable_client_throttling)
        packet += struct.pack("<B", self.client_throttle_threshold)
        packet += struct.pack("<f", self.client_throttle_scalar)
        packet += struct.pack("<B", 0)
        packet += struct.pack("<B", 0)
    
        self.server.logger.debug(f"📦 Network Settings Raw Data (Final+Fix): {binascii.hexlify(packet).decode()}")
    
        self.server.send(packet, connection.address)
        self.server.logger.info(f"✅ Sent Network Settings to {connection.address}"
