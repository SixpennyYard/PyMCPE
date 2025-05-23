import logging
import random
import socket
import sys
import time
import select

from pieraknet.handlers.offline_ping import OfflinePingHandler
from pieraknet.handlers.open_connection_request_1 import OpenConnectionRequest1Handler
from pieraknet.handlers.open_connection_request_2 import OpenConnectionRequest2Handler
from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.packets.open_connection_request_1 import OpenConnectionRequest1
from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.protocol_info import ProtocolInfo


class ConnectionNotFound(Exception):
    pass


class Server:
    def __init__(self, 
                 hostname="::",
                 port=19132, 
                 ipv=6, 
                 logger=None, 
                 logginglevel="INFO", 
                 game="MCPE", 
                 name="PieRakNet", 
                 game_protocol_version=776, 
                 version_name="1.21.60", 
                 max_player_count=20, 
                 modt="Powered by PieRakNet", 
                 game_mode="survival", 
                 game_mode_number=1, 
                 portv6=19133
                 ):
        self.loggingLevel = logginglevel
        if logger is None:
            logger = self.setup_logging()
        self.logger = logger
        self.hostname = hostname
        self.port = port
        self.ipv = ipv
        self.game = game
        self.name = name
        self.game_protocol_version = game_protocol_version
        self.version_name = version_name
        self.max_player_count = max_player_count
        self.server_id = "13253860892328930866"
        self.modt = modt
        self.game_mode = game_mode
        self.game_mode_number = game_mode_number
        self.portv6 = portv6
        self.raknet_protocol_version = 11
        self.guid = random.randint(0, sys.maxsize - 1)
        self.connections = []
        
        if self.ipv == 6:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            self.socket.bind((self.hostname, self.port, 0, 0))  # IPv6 bind
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.hostname, self.port))  # IPv4 bind

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.start_time = time.time()
        self.magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.running = False
        self.timeout = 15
        self.maxsize = 4096
        self.response_data = self.update_response_data()
        self.logger.info('Server initialized.')

    def setup_logging(self):
        logger = logging.getLogger("BedrockServer")
        logger.setLevel(logging.DEBUG) 

        formatter = logging.Formatter('%(asctime)s [%(name)s - %(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")

        file_handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.loggingLevel.upper()))  

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.debug("")
        logger.debug("")
        logger.debug("")

        return logger

    def send(self, data, address: tuple):
        if not isinstance(data, bytes):
            self.logger.debug(f"Encoding data to bytes: {data}")
            data = str(data).encode()
        self.logger.debug(f"Sending data to {address}")
        try:
            self.socket.sendto(data, address)
        except OSError as e:
            self.logger.error(f"Failed to send data to {address}: {e}")

    def update_response_data(self):
        player_count = len(self.connections)
        response_data = f"{self.game};{self.name};{self.game_protocol_version};{self.version_name};" \
               f"{player_count};{self.max_player_count};{self.server_id};{self.modt};" \
               f"{self.game_mode};{self.game_mode_number};{self.portv6};{self.port}"
        return response_data

    def get_connection(self, address):
        for connection in self.connections:
            if connection.address == address:
                return connection
        raise ConnectionNotFound()

    def add_connection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)
            self.update_response_data()
            self.logger.debug(f"Added connection: {connection} for address {connection.address}")
        else:
            self.logger.warning(f"Connection already exists: {connection.address}")

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            self.update_response_data()
            self.logger.debug(f"Removed connection: {connection} for address {connection.address}")
        else:
            self.logger.warning(f"Connection not found: {connection.address}")

    def start(self):
        self.running = True
        self.logger.info(f"Server started on {self.hostname}:{self.port}! (IPv{'6' if self.ipv == 6 else '4'})")

        while self.running:
            ready_sockets, _, _ = select.select([self.socket], [], [], 0.05)
            if self.socket in ready_sockets:
                try:
                    data, client = self.socket.recvfrom(self.maxsize)
                except OSError as e:
                    self.logger.warning(f"OS error while receiving data: {e}")
                    continue
                if data:
                    self.handle_data(data, client)

    def handle_data(self, data, client):
        packet_id = data[0]
        
        if packet_id in {ProtocolInfo.OFFLINE_PING, ProtocolInfo.OFFLINE_PING_OPEN_CONNECTIONS}:
            packet = OfflinePing(data)
            OfflinePingHandler.handle(packet, self, client)
        elif packet_id == ProtocolInfo.OPEN_CONNECTION_REQUEST_1:
            packet = OpenConnectionRequest1(data)
            OpenConnectionRequest1Handler.handle(packet, self, client)
        elif packet_id == ProtocolInfo.OPEN_CONNECTION_REQUEST_2:
            packet = OpenConnectionRequest2(data)
            OpenConnectionRequest2Handler.handle(packet, self, client)
        elif ProtocolInfo.FRAME_SET_0 <= packet_id <= ProtocolInfo.FRAME_SET_F:
            try:
                connection = self.get_connection(client)
                if hasattr(self, 'interface') and hasattr(self.interface, 'on_game_packet'):
                    self.interface.on_game_packet(data, connection)
            except ConnectionNotFound:
                self.logger.error(f"Connection not found for address {client}")

    def stop(self):
        self.running = False
        self.socket.close()
        self.logger.info('Server stopped.')
