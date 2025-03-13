import json
import base64
from bedrock_protocol.packets.login_packet import LoginPacket
from bedrock_protocol.utils import verify_xbox_certificate, verify_xbox_live
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class LoginManager:
    def __init__(self, server, player_manager, start_game):
        self.server = server
        self.player_manager = player_manager
        self.start_game = start_game

    def handle_login(self, data, connection):
        try:
            login_packet = LoginPacket(data)

            if login_packet.protocol != self.server.game_protocol_version:
                self.server.logger.warning(f"Login failed: Unsupported protocol {login_packet.protocol} from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if not login_packet.chain_data_jwt or not isinstance(login_packet.chain_data_jwt, list):
                self.server.logger.warning(f"Login failed: Invalid chainDataJwt from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if not verify_xbox_certificate(login_packet.chain_data_jwt):
                self.server.logger.warning(f"Login failed: Invalid Xbox Live certificate from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            client_data = json.loads(base64.b64decode(login_packet.client_data_jwt))
            username = client_data.get("DisplayName", "Unknown")
            uuid = client_data.get("ClientRandomId", "Unknown")
            xbox_token = client_data.get("XUID", None)

            self.server.logger.info(f"Player Info: {username} (UUID: {uuid}) | Xbox ID: {xbox_token} | IP: {connection.address}")

            if not xbox_token or not verify_xbox_live(xbox_token):
                self.server.logger.warning(f"Login failed: Invalid Xbox Live token from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if self.player_manager.is_banned(xbox_token):
                self.server.logger.warning(f"Login denied: BANNED PLAYER {username} (XUID: {xbox_token})")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if self.player_manager.is_whitelist_enabled() and not self.player_manager.is_whitelisted(xbox_token):
                self.server.logger.warning(f"Login denied: Player {username} (XUID: {xbox_token}) is not in the whitelist.")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            self.server.logger.info(f"LOGIN SUCCESS | {username} (UUID: {uuid}) | IP: {connection.address}")
            self.player_manager.add_player(connection, username, uuid)

            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_LOGIN_SUCCESS)
            self.start_game.send_start_game(connection, player_id=uuid)

        except Exception as e:
            self.server.logger.error(f"Failed to handle login: {e}")
            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)

        
    def send_play_status(self, connection, status):
        packet = bytes([BedrockProtocolInfo.PLAY_STATUS, status])
        self.server.send(packet, connection.address)
