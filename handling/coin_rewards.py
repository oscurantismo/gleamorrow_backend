import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from handling.user_coins import update_user_coins, get_user_coins, log_user_info

# ─── Mounted log directory ──────────────────────────────
BASE_DIR = "/mnt/data"
REWARD_LOG_PATH = os.path.join(BASE_DIR, "logs/reward_log.json")
coin_rewards = Blueprint('coins', __name__)

# ─── Coin values ────────────────────────────────────────
DIFFICULTY_COINS = {
    1: 10,
    2: 15,
    3: 25,
    4: 40,
}

# ─── Internal helpers ───────────────────────────────────
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

# ─── Core reward logic ──────────────────────────────────
def award_task_completion(user_id, task_name, difficulty, first_name=None, username=None):
    coins = DIFFICULTY_COINS.get(difficulty, 0)
    if coins <= 0:
        return 0

    # Save reward log
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
    update_user_coins(user_id, coins, first_name, username)

    # Log user info
    log_user_info(user_id, first_name, username)

    return coins

def get_reward_logs():
    ensure_file(REWARD_LOG_PATH, [])
    try:
        with open(REWARD_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        backup_path = REWARD_LOG_PATH.replace(
            ".json",
            f"_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_backup.json"
        )
        os.rename(REWARD_LOG_PATH, backup_path)
        with open(REWARD_LOG_PATH, "w") as f:
            json.dump([], f)
        print(f"[WARN] Corrupt log detected. Backed up to: {backup_path}")
        return []

# ─── API Route ──────────────────────────────────────────
@coin_rewards.route('/api/award-coins', methods=['POST'])
def award_coins():
    data = request.get_json()
    user_id = data.get('user_id')
    task_name = data.get('task_name')
    difficulty = int(data.get('difficulty', 0))
    first_name = data.get('first_name')
    username = data.get('username')

    if not user_id or not task_name:
        return jsonify({'error': 'Missing user_id or task_name'}), 400

    coins_awarded = award_task_completion(user_id, task_name, difficulty, first_name, username)

    return jsonify({'status': 'success', 'coins': coins_awarded})
