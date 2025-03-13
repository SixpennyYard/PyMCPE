import struct
import json
import base64

class LoginPacket:
    def __init__(self, data):
        self.protocol = None
        self.chain_data_jwt = None
        self.client_data_jwt = None

        self.parse_packet(data)

    def parse_packet(self, data):
        try:
            self.protocol = struct.unpack("<I", data[:4])[0]
            data = data[4:]

            connection_request_length, data = self.read_varint(data)
            connection_request = data[:connection_request_length].decode('utf-8')
            data = data[connection_request_length:]

            chain_data_json = json.loads(connection_request)
            if "chain" not in chain_data_json or not isinstance(chain_data_json["chain"], list):
                raise ValueError("Invalid chainDataJwt format")

            self.chain_data_jwt = chain_data_json["chain"]

            client_data_length, data = self.read_varint(data)
            self.client_data_jwt = data[:client_data_length].decode('utf-8')

        except Exception as e:
            raise ValueError(f"Failed to parse Login Packet: {e}")

    def read_varint(self, data):
        value = 0
        for i in range(5):
            byte = data[i]
            value |= (byte & 0x7F) << (7 * i)
            if not (byte & 0x80):
                return value, data[i+1:]
        raise ValueError("VarInt trop long")
