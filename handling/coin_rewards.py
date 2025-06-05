import os
import json
from datetime import datetime
from routes.coins import log_coin_reward

REWARD_LOG_PATH = "logs/reward_log.json"
USER_COIN_PATH = "logs/user_coins.json"

# Coin values by difficulty
DIFFICULTY_COINS = {
    1: 10,
    2: 15,
    3: 25,
    4: 40,
}


def ensure_file(path, default):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)


def load_json(path, fallback):
    ensure_file(path, fallback)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        with open(path, "w") as f:
            json.dump(fallback, f)
        return fallback


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def award_task_completion(user_id, task_name, difficulty):
    coins = DIFFICULTY_COINS.get(difficulty, 0)
    if coins <= 0:
        return 0

    # Log reward
    reward_log = load_json(REWARD_LOG_PATH, [])
    reward_log.append({
        "user_id": user_id,
        "task_name": task_name,
        "difficulty": difficulty,
        "coins": coins,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_json(REWARD_LOG_PATH, reward_log)

    # Update user coin total
    user_coins = load_json(USER_COIN_PATH, {})
    user_id = str(user_id)
    user_coins[user_id] = user_coins.get(user_id, 40) + coins
    save_json(USER_COIN_PATH, user_coins)

    update_user_coins(user_id, coins)
    log_coin_reward(user_id, task_name, difficulty, coins)
    return coins


def get_user_coins(user_id):
    user_coins = load_json(USER_COIN_PATH, {})
    return user_coins.get(str(user_id), 40)


def get_reward_logs():
    ensure_file(REWARD_LOG_PATH, [])
    try:
        with open(REWARD_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        backup_path = REWARD_LOG_PATH.replace(".json", f"_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_backup.json")
        os.rename(REWARD_LOG_PATH, backup_path)
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)
        print(f"[WARN] Corrupt log detected. Backed up to: {backup_path}")
        return []

