from bedrock_protocol.protocol.bedrock_protocol_info import BedrockProtocolInfo
import json
import base64

class BedrockProtocol:
    def __init__(self, server):
        self.server = server
        self.players = {}

    def on_game_packet(self, packet_body, connection):
        packet_id = packet_body[0]

        if packet_id == BedrockProtocolInfo.LOGIN:
            self.handle_login(packet_body, connection)
        elif packet_id == BedrockProtocolInfo.DISCONNECT:
            self.handle_disconnect(connection)
        else:
            self.server.logger.info(f"Unhandled packet: {packet_id} from {connection.address}")


    def handle_login(self, data, connection):
        try:
            data_length = data[1] 

            json_data_encoded = data[2:2 + data_length].decode('utf-8')
            json_data = json.loads(base64.b64decode(json_data_encoded))

            username = json_data.get("DisplayName", "Unknown")
            uuid = json_data.get("ClientRandomId", "Unknown")

            self.server.logger.info(f"New login: {username} (UUID: {uuid}) from {connection.address}")

            self.players[connection.address] = {"username": username, "uuid": uuid}

            self.send_play_status(connection, BedrockProtocolInfo.PLAY_STATUS_LOGIN_SUCCESS)

        except Exception as e:
            self.server.logger.error(f"Failed to parse login packet: {e}")

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