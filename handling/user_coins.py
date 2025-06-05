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
    with open(USER_DATA_PATH, "r+") as f:
        data = json.load(f)
        if str(user_id) not in data:
            data[str(user_id)] = 4000  # First launch bonus
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            print(f"[INFO] 🎉 New user {user_id} granted 4000 coins")
        return data[str(user_id)]


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
