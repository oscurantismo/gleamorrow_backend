from flask import Blueprint, request, Response
from handling.coin_rewards import get_reward_logs
import os
import base64
import json

debug_logs = Blueprint("debug_logs", __name__)

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

    # HTML content with embedded style and JS
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Logs</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f8f8f8;
                margin: 0;
                padding: 20px;
                color: #222;
            }}
            h1 {{
                color: #444;
            }}
            .nav {{
                margin-bottom: 20px;
            }}
            .nav button {{
                margin-right: 10px;
                padding: 8px 16px;
                background: #444;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            .nav button.active {{
                background: #222;
            }}
            .log-entry {{
                background: white;
                padding: 12px;
                margin-bottom: 10px;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .log-entry pre {{
                margin: 0;
                white-space: pre-wrap;
            }}
        </style>
        <script>
            function showLogs(type) {{
                document.querySelectorAll(".log-type").forEach(el => el.style.display = "none");
                document.getElementById(type).style.display = "block";

                document.querySelectorAll(".nav button").forEach(btn => btn.classList.remove("active"));
                document.getElementById(type + "-btn").classList.add("active");
            }}
        </script>
    </head>
    <body>
        <h1>🛠 Debug Logs</h1>
        <div class="nav">
            <button id="rewards-btn" class="active" onclick="showLogs('rewards')">🎁 Coin Rewards</button>
            <button id="other-btn" onclick="showLogs('other')">📦 Other Logs</button>
        </div>

        <div id="rewards" class="log-type">
            {''.join(f'''
            <div class="log-entry">
                <strong>User:</strong> {entry.get('user_id')}<br>
                <strong>Task:</strong> {entry.get('task_name')}<br>
                <strong>Difficulty:</strong> {entry.get('difficulty')}<br>
                <strong>Coins:</strong> {entry.get('coins')}<br>
                <strong>Timestamp:</strong> {entry.get('timestamp')}
            </div>''' for entry in logs)}
        </div>

        <div id="other" class="log-type" style="display:none;">
            <p>No other log types available yet.</p>
        </div>
    </body>
    </html>
    """

    return Response(html, mimetype="text/html")
