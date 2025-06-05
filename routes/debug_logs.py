# routes/debug_logs.py
from flask import Blueprint, request, jsonify
from logging.reward_logger import get_reward_logs

debug_logs = Blueprint("debug_logs", __name__)

# Simple token-based authentication
AUTHORIZED_TOKEN = os.environ.get("DEBUG_ADMIN_TOKEN")

@debug_logs.route("/debug-logs", methods=["GET"])
def debug_logs_page():
    token = request.args.get("token")
    if token != AUTHORIZED_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    logs = get_reward_logs()
    return jsonify(logs)
