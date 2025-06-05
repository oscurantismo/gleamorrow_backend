import os
import json
import shutil
from datetime import datetime
from flask import Blueprint, request, jsonify

tasks = Blueprint("tasks", __name__)

# ─── Mounted volume base path ───────────────────────────
BASE_DIR = "/mnt/data"
TASKS_PATH = os.path.join(BASE_DIR, "data/user_tasks.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
USER_LOG_PATH = os.path.join(BASE_DIR, "logs/user_info.json")

# ─── Internal utilities ─────────────────────────────────
def ensure_file():
    os.makedirs(os.path.dirname(TASKS_PATH), exist_ok=True)
    if not os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, "w") as f:
            json.dump({}, f)

def load_tasks():
    ensure_file()
    with open(TASKS_PATH, "r") as f:
        return json.load(f)

def save_tasks(data):
    with open(TASKS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def backup_tasks():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"tasks_backup_{timestamp}.json")
    shutil.copy(TASKS_PATH, backup_path)
    print(f"[INFO] ✅ Task backup saved: {backup_path}")

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
        data[user_id]["last_task_update"] = datetime.utcnow().isoformat()

        with open(USER_LOG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to log user info: {e}")

# ─── API Endpoints ──────────────────────────────────────
@tasks.route("/api/tasks", methods=["GET"])
def get_user_tasks():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    all_tasks = load_tasks()
    return jsonify(all_tasks.get(str(user_id), []))

@tasks.route("/api/tasks", methods=["POST"])
def save_user_tasks():
    data = request.get_json()
    user_id = str(data.get("user_id"))
    user_tasks = data.get("tasks", [])

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    all_tasks = load_tasks()
    all_tasks[user_id] = user_tasks
    save_tasks(all_tasks)
    backup_tasks()

    # Optional: log user info
    from handling.user_coins import log_user_info
    log_user_info(user_id, data.get("first_name"), data.get("username"))

    return jsonify({"status": "saved", "count": len(user_tasks)})
