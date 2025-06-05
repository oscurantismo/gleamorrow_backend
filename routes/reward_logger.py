import json
import os
from datetime import datetime

REWARD_LOG_PATH = "logs/reward_log.json"

def ensure_log_file():
    """Ensure the log file and directory exist and contain valid JSON."""
    # Ensure 'logs/' directory exists
    os.makedirs(os.path.dirname(REWARD_LOG_PATH), exist_ok=True)

    # If file doesn't exist, create it with empty list
    if not os.path.exists(REWARD_LOG_PATH):
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)
        return

    # If file exists but is invalid JSON or corrupted, back it up and reset
    try:
        with open(REWARD_LOG_PATH, "r") as f:
            json.load(f)
    except (json.JSONDecodeError, ValueError):
        backup_path = REWARD_LOG_PATH.replace(".json", f"_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_backup.json")
        os.rename(REWARD_LOG_PATH, backup_path)
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)
        print(f"[WARN] Corrupt log detected. Backed up to: {backup_path}")

def log_coin_reward(user_id, task_name, difficulty, coins):
    """Add a coin reward entry to the log."""
    ensure_log_file()

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "task": task_name,
        "difficulty": difficulty,
        "coins_awarded": coins
    }

    try:
        with open(REWARD_LOG_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[ERROR] Failed to log reward: {e}")

def get_reward_logs():
    """Return all reward logs as a list."""
    ensure_log_file()
    try:
        with open(REWARD_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read reward log: {e}")
        return []
