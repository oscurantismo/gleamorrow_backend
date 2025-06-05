from flask import Blueprint, request, Response
from handling.coin_rewards import get_reward_logs
import os
import base64
import json
import glob

debug_logs = Blueprint("debug_logs", __name__)

DEBUG_ADMIN_USER = os.environ.get("DEBUG_ADMIN_USER", "admin")
DEBUG_ADMIN_PASS = os.environ.get("DEBUG_ADMIN_PASS", "password")

USER_LOG_PATH = "logs/user_info.json"
TASKS_PATH = "data/user_tasks.json"  # ✅ Live task data
TASK_BACKUP_PATH = "backups/tasks_backup_*.json"
COIN_BACKUP_PATH = "backups/coins_backup_*.json"

def check_auth(auth_header):
    if not auth_header:
        return False
    try:
        scheme, b64 = auth_header.split()
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(b64).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username == DEBUG_ADMIN_USER and password == DEBUG_ADMIN_PASS
    except Exception:
        return False

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def load_backups(pattern):
    files = sorted(glob.glob(pattern), reverse=True)
    data = []
    for path in files[:5]:  # Limit to latest 5 backups
        try:
            with open(path, "r") as f:
                content = json.load(f)
                data.append((os.path.basename(path), content))
        except:
            continue
    return data

@debug_logs.route("/debug-logs", methods=["GET"])
def debug_logs_page():
    auth_header = request.headers.get("Authorization")
    if not check_auth(auth_header):
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login required"'})

    reward_logs = get_reward_logs()
    user_logs = load_json(USER_LOG_PATH, {})
    current_tasks = load_json(TASKS_PATH, {})  # ✅ Live task state
    task_backups = load_backups(TASK_BACKUP_PATH)
    coin_backups = load_backups(COIN_BACKUP_PATH)

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
            h1 {{ color: #444; }}
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
            .nav button.active {{ background: #222; }}
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
                font-size: 13px;
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
            <button id="users-btn" onclick="showLogs('users')">👤 User Info</button>
            <button id="current-tasks-btn" onclick="showLogs('current-tasks')">📄 Current Tasks</button>
            <button id="tasks-btn" onclick="showLogs('tasks')">📝 Task Backups</button>
            <button id="coins-btn" onclick="showLogs('coins')">🪙 Coin Backups</button>
        </div>

        <div id="rewards" class="log-type">
            {''.join(f'''
            <div class="log-entry">
                <strong>User:</strong> {entry.get('user_id')}<br>
                <strong>Task:</strong> {entry.get('task_name')}<br>
                <strong>Difficulty:</strong> {entry.get('difficulty')}<br>
                <strong>Coins:</strong> {entry.get('coins')}<br>
                <strong>Timestamp:</strong> {entry.get('timestamp')}
            </div>''' for entry in reward_logs)}
        </div>

        <div id="users" class="log-type" style="display:none;">
            {''.join(f'''
            <div class="log-entry">
                <strong>User ID:</strong> {uid}<br>
                <strong>First Name:</strong> {info.get("first_name")}<br>
                <strong>Username:</strong> {info.get("username")}<br>
                <strong>Last Seen:</strong> {info.get("last_seen", info.get("last_coin_update", info.get("last_task_update", "N/A")))}
            </div>''' for uid, info in user_logs.items())}
        </div>

        <div id="current-tasks" class="log-type" style="display:none;">
            <div class="log-entry">
                <strong>File:</strong> user_tasks.json<br>
                <pre>{json.dumps(current_tasks, indent=2)[:2000]}</pre>
            </div>
        </div>

        <div id="tasks" class="log-type" style="display:none;">
            {''.join(f'''
            <div class="log-entry">
                <strong>File:</strong> {fname}<br>
                <pre>{json.dumps(content, indent=2)[:1000]}</pre>
            </div>''' for fname, content in task_backups)}
        </div>

        <div id="coins" class="log-type" style="display:none;">
            {''.join(f'''
            <div class="log-entry">
                <strong>File:</strong> {fname}<br>
                <pre>{json.dumps(content, indent=2)[:1000]}</pre>
            </div>''' for fname, content in coin_backups)}
        </div>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")
