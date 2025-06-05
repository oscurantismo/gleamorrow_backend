from flask import Blueprint, request, jsonify
import os, json
from datetime import datetime

coins = Blueprint('coins', __name__)

DIFFICULTY_COINS = {
    1: 10,
    2: 15,
    3: 25,
    4: 40,
}

def award_task_completion(user_id, task_name, difficulty):
    from handling.user_coins import update_user_coins
    coins = DIFFICULTY_COINS.get(difficulty, 0)
    if coins <= 0:
        return 0

    update_user_coins(user_id, coins)
    log_coin_reward(user_id, task_name, difficulty, coins)
    return coins


@coins.route('/api/award-coins', methods=['POST'])
def award_coins():
    
    data = request.get_json()
    user_id = data.get('user_id')
    task_name = data.get('task_name')
    difficulty = int(data.get('difficulty', 0))
    coins_awarded = award_task_completion(user_id, task_name, difficulty)
    return jsonify({'status': 'success', 'coins': coins_awarded})


REWARD_LOG_PATH = "logs/reward_log.json"

def ensure_log_file():
    os.makedirs(os.path.dirname(REWARD_LOG_PATH), exist_ok=True)
    if not os.path.exists(REWARD_LOG_PATH):
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)

def log_coin_reward(user_id, task_name, difficulty, coins):
    os.makedirs(os.path.dirname(REWARD_LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "task_name": task_name,
        "difficulty": difficulty,
        "coins": coins
    }
    try:
        with open(REWARD_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to append reward log: {e}")


def get_reward_logs():
    if not os.path.exists(REWARD_LOG_PATH):
        return []

    try:
        with open(REWARD_LOG_PATH, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"[ERROR] Failed to parse reward logs: {e}")
        return []
