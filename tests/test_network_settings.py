import unittest
from unittest.mock import MagicMock
from bedrock_protocol.packets.network_settings import NetworkSettings

class TestNetworkSettings(unittest.TestCase):
    def setUp(self):
        self.mock_server = MagicMock()
        self.mock_server.logger = MagicMock()

        self.network_settings = NetworkSettings(self.mock_server)

    def test_packet_structure(self):
        connection = MagicMock()
        connection.address = ("127.0.0.1", 12345)

        self.network_settings.handle_request(connection)

        self.mock_server.logger.info.assert_called()
        self.mock_server.send.assert_called()

if __name__ == '__main__':
    unittest.main()
