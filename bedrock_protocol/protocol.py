from pieraknet.protocol_info import ProtocolInfo

class BedrockProtocol:
    def __init__(self, server):
        self.server = server
        self.players = {}

    def on_game_packet(self, packet_body, connection):
        packet_id = packet_body[0]

        if packet_id == ProtocolInfo.LOGIN:
            self.handle_login(packet_body, connection)
        else:
            self.server.logger.info(f"Unhandled packet: {packet_id} from {connection.address}")

    def handle_login(self, data, connection):
        username = "Unknown"  
        self.server.logger.info(f"New login from {connection.address}: {username}")

        self.players[connection.address] = {"username": username}

        self.send_play_status(connection, ProtocolInfo.PLAY_STATUS_LOGIN_SUCCESS)

    def send_play_status(self, connection, status):
        packet = bytes([ProtocolInfo.PLAY_STATUS, status])
        self.server.send(packet, connection.address)
