from pieraknet.server import Server as RakNetServer

class BedrockServer:
    def main(self):
        from bedrock_protocol import BedrockProtocol

        server = RakNetServer(logginglevel="INFO")
        protocol = BedrockProtocol(server)
        server.interface = protocol

        server.start()


if __name__ == '__main__':
    server = BedrockServer()
    server.main()


