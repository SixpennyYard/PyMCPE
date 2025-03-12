import struct

from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class StartGame:
    def __init__(self, server):
        self.server = server

    def send_start_game(self, connection, player_id):
        self.server.logger.info(f"Sending Start Game to {connection.address}")

        #TODO: create a better world system
        spawn_x = 0.0
        spawn_y = 64.0
        spawn_z = 0.0

        packet = struct.pack("<B", BedrockProtocolInfo.START_GAME)  
        packet += struct.pack("<Q", player_id)  
        packet += struct.pack("<iii", int(spawn_x), int(spawn_y), int(spawn_z))  
        packet += struct.pack("<f", spawn_x)  
        packet += struct.pack("<f", spawn_y) 
        packet += struct.pack("<f", spawn_z)  
        packet += struct.pack("<i", 123456) 
        packet += struct.pack("<B", 0) 
        packet += struct.pack("<B", 2) 

        self.server.send(packet, connection.address)
