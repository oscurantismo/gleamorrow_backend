from flask import Blueprint, request, jsonify
import os, json
from datetime import datetime

coins = Blueprint('coins', __name__)

@coins.route('/api/award-coins', methods=['POST'])
def award_coins():
    from handling.coin_rewards import award_task_completion  # ✅ Local import to avoid circular dependency

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
    ensure_log_file()
    try:
        with open(REWARD_LOG_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append({
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "task_name": task_name,
                "difficulty": difficulty,
                "coins": coins
            })
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[ERROR] Failed to log reward: {e}")

def get_reward_logs():
    ensure_log_file()
    try:
        with open(REWARD_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load reward logs: {e}")
        return []
