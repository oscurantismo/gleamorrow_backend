import os
import json

USER_DATA_PATH = "data/user_coins.json"

def ensure_user_file():
    os.makedirs(os.path.dirname(USER_DATA_PATH), exist_ok=True)
    if not os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "w") as f:
            json.dump({}, f)

def get_user_coins(user_id):
    ensure_user_file()
    with open(USER_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), 40)  # Default starting coins

def update_user_coins(user_id, coins_to_add):
    ensure_user_file()
    with open(USER_DATA_PATH, "r+") as f:
        data = json.load(f)
        current = data.get(str(user_id), 40)
        new_total = current + coins_to_add
        data[str(user_id)] = new_total
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    return new_total
