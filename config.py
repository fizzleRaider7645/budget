# config.py

import json

USER_CONFIG_FILE = "user_config.json"

def load_user_config():
    try:
        with open(USER_CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("❌ user_config.json not found.")
    except json.JSONDecodeError:
        raise ValueError("❌ user_config.json is malformed.")
