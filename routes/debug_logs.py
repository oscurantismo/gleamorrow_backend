# routes/debug_logs.py
from flask import Blueprint, request, jsonify, Response
from reward_logger import get_reward_logs
import os
import base64

debug_logs = Blueprint("debug_logs", __name__)

# Load credentials from Railway env vars
DEBUG_ADMIN_USER = os.environ.get("DEBUG_ADMIN_USER", "admin")
DEBUG_ADMIN_PASS = os.environ.get("DEBUG_ADMIN_PASS", "password")

def check_auth(auth_header):
    if not auth_header:
        return False

    try:
        scheme, b64credentials = auth_header.split()
        if scheme.lower() != "basic":
            return False

        decoded = base64.b64decode(b64credentials).decode("utf-8")
        username, password = decoded.split(":", 1)

        return username == DEBUG_ADMIN_USER and password == DEBUG_ADMIN_PASS
    except Exception:
        return False

@debug_logs.route("/debug-logs", methods=["GET"])
def debug_logs_page():
    auth_header = request.headers.get("Authorization")

    if not check_auth(auth_header):
        return Response(
            "Unauthorized",
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="Login required"'}
        )

    logs = get_reward_logs()
    return jsonify(logs)
