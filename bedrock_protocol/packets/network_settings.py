import struct

from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class NetworkSettings:
    def __init__(self, server):
        self.server = server

    def handle_request(self, connection):
        self.server.logger.info(f"Received Request Network Settings from {connection.address}")

        flags = struct.pack("<I", 0) 

        options = [
            1,
            2, 
            3  
        ]

        encoded_options = b"".join(self.encode_varint(option) for option in options)

        response_packet = bytes([BedrockProtocolInfo.NETWORK_SETTINGS]) + flags + self.encode_varint(len(options)) + encoded_options

        self.server.send(response_packet, connection.address)
        self.server.logger.info(f"Sent Network Settings to {connection.address}")

    def encode_varint(self, value):
        encoded = b""
        while value >= 0x80:
            encoded += bytes([(value & 0x7F) | 0x80])
            value >>= 7
        encoded += bytes([value])
        return encoded