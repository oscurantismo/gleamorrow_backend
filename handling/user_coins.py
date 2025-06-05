import os
import json
import shutil
from utils.backup_rotation import rotate_backups
from datetime import datetime

# ─── Mounted volume base path ───────────────────────────
BASE_DIR = "/mnt/data"
USER_DATA_PATH = os.path.join(BASE_DIR, "data/user_coins.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
USER_LOG_PATH = os.path.join(BASE_DIR, "logs/user_info.json")
MAX_BACKUPS = 5

# ─── Ensure coin file exists ────────────────────────────
def ensure_user_file():
    os.makedirs(os.path.dirname(USER_DATA_PATH), exist_ok=True)
    if not os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "w") as f:
            json.dump({}, f)

# ─── Backup coin file safely ────────────────────────────
def backup_user_coins():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"coins_backup_{timestamp}.json")
    shutil.copy(USER_DATA_PATH, backup_path)
    print(f"[INFO] ✅ Coin backup saved: {backup_path}")
    rotate_backups(BACKUP_DIR, "coins_backup_*.json", MAX_BACKUPS)

# ─── User metadata logging ──────────────────────────────
def log_user_info(user_id, first_name=None, username=None):
    os.makedirs(os.path.dirname(USER_LOG_PATH), exist_ok=True)
    try:
        if os.path.exists(USER_LOG_PATH):
            with open(USER_LOG_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        if user_id not in data:
            data[user_id] = {}

        data[user_id]["first_name"] = first_name or data[user_id].get("first_name", "")
        data[user_id]["username"] = username or data[user_id].get("username", "")
        data[user_id]["last_coin_update"] = datetime.utcnow().isoformat()

        with open(USER_LOG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to log user info: {e}")

# ─── Coin access / creation logic ───────────────────────
def get_user_coins(user_id, first_name=None, username=None):
    ensure_user_file()
    with open(USER_DATA_PATH, "r+") as f:
        data = json.load(f)
        if str(user_id) not in data:
            data[str(user_id)] = 4000  # First launch bonus
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            print(f"[INFO] 🎉 New user {user_id} granted 4000 coins")
        log_user_info(user_id, first_name, username)
        return data[str(user_id)]

# ─── Coin update logic ──────────────────────────────────
def update_user_coins(user_id, coins_to_add, first_name=None, username=None):
    ensure_user_file()
    with open(USER_DATA_PATH, "r+") as f:
        data = json.load(f)
        current = data.get(str(user_id), 4000)
        new_total = current + coins_to_add
        data[str(user_id)] = new_total
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    backup_user_coins()
    log_user_info(user_id, first_name, username)
    return new_total
