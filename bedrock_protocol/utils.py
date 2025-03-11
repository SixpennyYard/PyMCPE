import json
import jwt
import requests
from jwt.algorithms import RSAAlgorithm


# ---- Constants ----
MICROSOFT_CERTS_URL = "https://xboxlive.com/keys"
XBOX_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
# TODO: move these to a proper file
WHITELIST_FILE = "whitelist.json"
BANNED_FILE = "banned.json"


# ---- JSON gestion ----
def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def ban_player(self, xuid, reason="No reason provided"):
    self.banned[xuid] = reason
    save_json_file(BANNED_FILE, self.banned)
    self.server.logger.info(f"Player {xuid} has been banned: {reason}")

def whitelist_player(self, xuid):
    self.whitelist[xuid] = True
    save_json_file(WHITELIST_FILE, self.whitelist)
    self.server.logger.info(f"Player {xuid} has been added to the whitelist.")

# ---- Microsoft Xbox Live verification ----
def get_microsoft_public_keys():
    try:
        response = requests.get(MICROSOFT_CERTS_URL)
        response.raise_for_status()
        return response.json() 
    except Exception as e:
        print(f"Failed to get Microsoft public keys: {e}")
        return None

def verify_xbox_certificate(self, identity_token):
    try:
        decoded_header = jwt.get_unverified_header(identity_token)
        kid = decoded_header.get("kid") 

        public_keys = get_microsoft_public_keys()
        if not public_keys or kid not in public_keys:
            return False

        public_key_pem = public_keys[kid]
        public_key = RSAAlgorithm.from_jwk(public_key_pem)


        jwt.decode(identity_token, public_key, algorithms=["RS256"], options={"verify_exp": True})
        return True 

    except jwt.ExpiredSignatureError:
        print("Token expiré")
    except jwt.InvalidTokenError:
        print("Token invalide")

    return False  

def verify_xbox_live(self, xbox_token):
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": xbox_token 
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }

        response = requests.post(XBOX_AUTH_URL, json=data, headers=headers)
        response_data = response.json()

        if "IssueInstant" in response_data:
            return True

    except Exception as e:
        self.server.logger.error(f"Xbox Live verification failed: {e}")

    return False

