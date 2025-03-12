from bedrock_protocol.utils import BANNED_FILE, WHITELIST_FILE, load_json_file, verify_xbox_certificate, verify_xbox_live
from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo
import json
import base64
import threading
import time


class BedrockProtocol:

    TIMEOUT_SECONDS = 30 

    def __init__(self, server):
        self.server = server
        self.players = {}
        self.whitelist = load_json_file(WHITELIST_FILE)
        self.banned = load_json_file(BANNED_FILE)

        self.start_timeout_checker()


    def on_game_packet(self, packet_body, connection):
        if connection.address in self.players:
            self.players[connection.address]["last_activity"] = time.time()

        packet_id = packet_body[0]

        if packet_id not in vars(BedrockProtocolInfo).values():
            self.server.logger.warning(f"Received unknown packet ID: {packet_id} from {connection.address}")


        if packet_id == BedrockProtocolInfo.LOGIN:
            self.handle_login(packet_body, connection)
        elif packet_id == BedrockProtocolInfo.DISCONNECT:
            self.handle_disconnect(connection)


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
            
            if not xbox_token:
                self.server.logger.warning(f"Login failed: No Xbox Live token from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return
            if not verify_xbox_live(xbox_token):
                self.server.logger.warning(f"Login failed: Invalid Xbox Live token from {connection.address}")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            if xbox_token in self.banned:
                self.server.logger.warning(f"Login failed: Banned player {username} (XUID: {xbox_token}) tried to join.")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return
            if self.whitelist and xbox_token not in self.whitelist:
                self.server.logger.warning(f"Login failed: Player {username} (XUID: {xbox_token}) is not in the whitelist.")
                self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)
                return

            self.server.logger.info(f"New login: {username} (UUID: {uuid}) from {connection.address}")

            self.players[connection.address] = {"username": username, "uuid": uuid, "last_activity": time.time()}

            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_LOGIN_SUCCESS)

        except Exception as e:
            self.server.logger.error(f"Failed to parse login packet: {e}")
            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_FAILED_CLIENT)

    def handle_disconnect(self, connection):
        address = connection.address

        if address in self.players:
            player = self.players.pop(address)
            self.server.logger.info(f"Player {player['username']} disconnected from {address}")
        else:
            self.server.logger.warning(f"Received DISCONNECT from unknown address: {address}")

    def send_play_status(self, connection, status):
        packet = bytes([BedrockProtocolInfo.PLAY_STATUS, status])
        self.server.send(packet, connection.address)

    def check_for_timeouts(self):
        current_time = time.time()
        to_remove = []

        for address, player in self.players.items():
            if current_time - player["last_activity"] > BedrockProtocol.TIMEOUT_SECONDS:
                to_remove.append(address)

        for address in to_remove:
            player = self.players.pop(address)
            self.server.logger.info(f"Timeout: Player {player['username']} (UUID: {player['uuid']}) disconnected due to inactivity.")

    def start_timeout_checker(self):
        def timeout_loop():
            while True:
                self.check_for_timeouts()
                time.sleep(5)

        thread = threading.Thread(target=timeout_loop, daemon=True)
        thread.start()
