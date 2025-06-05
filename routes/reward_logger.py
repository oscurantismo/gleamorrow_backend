# reward_logger.py
import json
import os
from datetime import datetime

REWARD_LOG_PATH = "logs/reward_log.json"

def ensure_log_file():
    if not os.path.exists(REWARD_LOG_PATH):
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)

def log_coin_reward(user_id, task_name, difficulty, coins):
    ensure_log_file()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "task": task_name,
        "difficulty": difficulty,
        "coins_awarded": coins
    }
    with open(REWARD_LOG_PATH, "r+") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def get_reward_logs():
    ensure_log_file()
    with open(REWARD_LOG_PATH, "r") as f:
        return json.load(f)
