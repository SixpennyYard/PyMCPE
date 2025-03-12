from pieraknet.server import Server as RakNetServer

class BedrockServer:
    def main(self):
        from bedrock_protocol.protocol.protocol import BedrockProtocol

        print(0x80 <= 0x01)
        server = RakNetServer(logginglevel="INFO", hostname="127.0.0.1", ipv=4)
        protocol = BedrockProtocol(server)
        server.interface = protocol

        server.start()


if __name__ == '__main__':
    server = BedrockServer()
    server.main()


