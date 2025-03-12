from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo
from bedrock_protocol.manager.compression_manager import CompressionManager
from bedrock_protocol.packets.network_settings import NetworkSettings
from bedrock_protocol.packets.start_game import StartGame
from bedrock_protocol.manager.login_manager import LoginManager
from bedrock_protocol.manager.player_manager import PlayerManager
import time

class BedrockProtocol:
    def __init__(self, server):
        self.server = server
        self.player_manager = PlayerManager(server)
        self.network_settings = NetworkSettings(server)
        self.compression = CompressionManager(server)
        self.start_game = StartGame(server)
        self.login_manager = LoginManager(server, self.player_manager, self.start_game)

    def on_game_packet(self, packet_body, connection):
        self.player_manager.update_activity(connection)
        packet_id = packet_body[0]

        if packet_id not in vars(BedrockProtocolInfo).values():
            self.server.logger.warning(f"❓ Unknown packet ID: {packet_id} from {connection.address}")
            return

        if packet_id == BedrockProtocolInfo.LOGIN:
            self.login_manager.handle_login(packet_body, connection)
        elif packet_id == BedrockProtocolInfo.DISCONNECT:
            self.player_manager.remove_player(connection)
        elif packet_id == BedrockProtocolInfo.REQUEST_NETWORK_SETTINGS:
            self.network_settings.handle_request(connection)
        elif packet_id == BedrockProtocolInfo.COMPRESSED_PACKET:
            decompressed_data = self.compression.decompress(packet_body[1:])
            if decompressed_data:
                packet_body = decompressed_data
                packet_id = packet_body[0]
                self.server.logger.info(f"📦 Decompressed packet {packet_id} from {connection.address}")
