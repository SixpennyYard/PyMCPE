import struct
import binascii
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class NetworkSettings:
    def __init__(self, server):
        self.server = server

        self.compression_threshold = 1
        self.compression_algorithm = 0
        self.enable_client_throttling = False
        self.client_throttle_threshold = 0
        self.client_throttle_scalar = 0

    def handle_request(self, connection):
        self.server.logger.info(f"📡 Received Request Network Settings from {connection.address}")
    
        packet = struct.pack("<B", BedrockProtocolInfo.NETWORK_SETTINGS)
        packet += struct.pack("<H", self.compression_threshold)
        packet += struct.pack("<H", self.compression_algorithm)
        packet += struct.pack("<?", self.enable_client_throttling)
        packet += struct.pack("<B", self.client_throttle_threshold)
        packet += struct.pack(">f", self.client_throttle_scalar)

        self.server.logger.debug(f"compressionThreshold: {self.compression_threshold}")
        self.server.logger.debug(f"compressionAlgorithm: {self.compression_algorithm}")
        self.server.logger.debug(f"enableClientThrottling: {self.enable_client_throttling}")
        self.server.logger.debug(f"clientThrottleThreshold: {self.client_throttle_threshold}")
        self.server.logger.debug(f"clientThrottleScalar: {self.client_throttle_scalar}")
        self.server.logger.debug(f"📦 Network Settings Raw Data (Final+Fix): {binascii.hexlify(packet).decode()}")
    
        self.server.send(packet, connection.address)
        self.server.logger.info(f"✅ Sent Network Settings to {connection.address}")
