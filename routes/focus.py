import os
import json
from flask import Blueprint, request, jsonify
from datetime import datetime

focus = Blueprint("focus", __name__)

BASE_DIR = "/mnt/data"
FOCUS_PATH = os.path.join(BASE_DIR, "data/focus_data.json")

def load_focus_data():
    if not os.path.exists(FOCUS_PATH):
        return {}
    with open(FOCUS_PATH, "r") as f:
        return json.load(f)

def save_focus_data(data):
    os.makedirs(os.path.dirname(FOCUS_PATH), exist_ok=True)
    with open(FOCUS_PATH, "w") as f:
        json.dump(data, f, indent=2)

@focus.route("/api/focus/update", methods=["POST"])
def update_focus_data():
    payload = request.json

    user_id = str(payload.get("user_id"))
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        minutes = int(payload.get("minutes", 0))
        if minutes < 0:
            raise ValueError("Negative minutes")
    except Exception as e:
        print("Invalid minutes:", e)
        return jsonify({"error": "Invalid minutes"}), 400

    try:
        unlocked = int(payload.get("flowers_unlocked", 0)) if payload.get("flowers_unlocked") is not None else 0
    except Exception as e:
        print("Invalid flowers_unlocked:", e)
        unlocked = 0

    flowers = payload.get("flowers", [])

    data = load_focus_data()

    if user_id not in data:
        data[user_id] = {
            "total_minutes": 0,
            "sessions_completed": 0,
            "flowers_unlocked": 0,
            "flowers": {}
        }

    if "flowers" not in data[user_id]:
        data[user_id]["flowers"] = {}

    for flower in flowers:
        fname = flower.get("name")
        ts = flower.get("timestamp") or datetime.utcnow().isoformat()
        if fname and fname not in data[user_id]["flowers"]:
            data[user_id]["flowers"][fname] = ts

    data[user_id]["total_minutes"] += minutes
    data[user_id]["sessions_completed"] += 1
    data[user_id]["flowers_unlocked"] = max(data[user_id]["flowers_unlocked"], unlocked)

    save_focus_data(data)
    return jsonify({"success": True, "data": data[user_id]})

@focus.route("/api/focus/stats", methods=["GET"])
def get_focus_stats():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    data = load_focus_data()
    stats = data.get(user_id, {
        "total_minutes": 0,
        "sessions_completed": 0,
        "flowers_unlocked": 0,
        "flowers": {}
    })

    return jsonify(stats)
