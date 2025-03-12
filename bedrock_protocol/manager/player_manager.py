import time
import threading
from bedrock_protocol.utils import BANNED_FILE, WHITELIST_FILE, load_json_file

class PlayerManager:
    TIMEOUT_SECONDS = 30

    def __init__(self, server):
        self.server = server
        self.players = {}
        self.whitelist = load_json_file(WHITELIST_FILE)
        self.banned = load_json_file(BANNED_FILE)
        self.start_timeout_checker()

    def add_player(self, connection, username, uuid):
        self.players[connection.address] = {"username": username, "uuid": uuid, "last_activity": time.time()}

    def remove_player(self, connection):
        address = connection.address
        if address in self.players:
            player = self.players.pop(address)
            self.server.logger.info(f"🚪 Player {player['username']} disconnected from {address}")

    def is_banned(self, xbox_token):
        return xbox_token in self.banned

    def is_whitelisted(self, xbox_token):
        return xbox_token in self.whitelist

    def is_whitelist_enabled(self):
        return bool(self.whitelist)

    def update_activity(self, connection):
        if connection.address in self.players:
            self.players[connection.address]["last_activity"] = time.time()

    def check_for_timeouts(self):
        current_time = time.time()
        to_remove = [addr for addr, p in self.players.items() if current_time - p["last_activity"] > self.TIMEOUT_SECONDS]
        
        for address in to_remove:
            self.remove_player_by_address(address)

    def remove_player_by_address(self, address):
        if address in self.players:
            player = self.players.pop(address)
            self.server.logger.info(f"⏳ Timeout: Player {player['username']} (UUID: {player['uuid']}) disconnected due to inactivity.")

    def start_timeout_checker(self):
        def timeout_loop():
            while True:
                self.check_for_timeouts()
                time.sleep(5)

        threading.Thread(target=timeout_loop, daemon=True).start()
