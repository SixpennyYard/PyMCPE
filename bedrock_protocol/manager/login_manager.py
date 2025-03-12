import json
import base64
from bedrock_protocol.utils import verify_xbox_certificate, verify_xbox_live
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo

class LoginManager:
    def __init__(self, server, player_manager, start_game):
        self.server = server
        self.player_manager = player_manager
        self.start_game = start_game

    def handle_login(self, data, connection):
        try:
            data_length = data[1]
            json_data_encoded = data[2:2 + data_length].decode('utf-8')
            json_data = json.loads(base64.b64decode(json_data_encoded))

            identity_token = json_data.get("identityPublicKey", "")
            client_data_encoded = json_data.get("clientData", "")

            if not identity_token or not client_data_encoded or not verify_xbox_certificate(identity_token):
                self.server.logger.warning(f"Login failed: Unverified Xbox identity from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            client_data = json.loads(base64.b64decode(client_data_encoded))
            username = client_data.get("DisplayName", "Unknown")
            uuid = client_data.get("ClientRandomId", "Unknown")
            xbox_token = client_data.get("XUID", None)

            self.server.logger.info(f"Client version: {client_data.get('GameVersion', 'Unknown')}")

            if not xbox_token or not verify_xbox_live(xbox_token):
                self.server.logger.warning(f"Login failed: Invalid Xbox Live token from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if self.player_manager.is_banned(xbox_token):
                self.server.logger.warning(f"Login failed: Banned player {username} (XUID: {xbox_token}) tried to join.")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if self.player_manager.is_whitelist_enabled() and not self.player_manager.is_whitelisted(xbox_token):
                self.server.logger.warning(f"Login failed: Player {username} (XUID: {xbox_token}) is not in the whitelist.")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            self.server.logger.info(f"✅ LOGIN SUCCESS | {username} (UUID: {uuid}) | IP: {connection.address}")

            self.player_manager.add_player(connection, username, uuid)
            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_LOGIN_SUCCESS)
            self.start_game.send_start_game(connection, player_id=uuid)

        except Exception as e:
            self.server.logger.error(f"❌ Failed to parse login packet: {e}")
            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)

    def send_play_status(self, connection, status):
        packet = bytes([BedrockProtocolInfo.PLAY_STATUS, status])
        self.server.send(packet, connection.address)
