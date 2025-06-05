from flask import Blueprint, request, jsonify
import os
import json

tasks = Blueprint("tasks", __name__)
TASKS_PATH = "data/user_tasks.json"

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
    tasks = data.get("tasks", [])

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    all_tasks = load_tasks()
    all_tasks[user_id] = tasks
    save_tasks(all_tasks)

    return jsonify({"status": "saved", "count": len(tasks)})
