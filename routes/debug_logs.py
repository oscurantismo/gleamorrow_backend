import os
import json
import base64
from flask import Blueprint, request, Response, send_file
from handling.coin_rewards import get_reward_logs
from utils.backup_utils import (
    list_backups,
    load_backup_content,
    save_manual_backup,
    replace_data_file,
    get_file_path_for_type
)

debug_logs = Blueprint("debug_logs", __name__)

DEBUG_ADMIN_USER = os.environ.get("DEBUG_ADMIN_USER")
DEBUG_ADMIN_PASS = os.environ.get("DEBUG_ADMIN_PASS")
BASE_DIR = "/mnt/data"

USER_LOG_PATH = os.path.join(BASE_DIR, "logs/user_info.json")
TASKS_PATH = os.path.join(BASE_DIR, "data/user_tasks.json")
FOCUS_PATH = os.path.join(BASE_DIR, "data/focus_data.json")

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

def format_backup_html(prefix):
    entries = list_backups(prefix)
    html = ""
    for path in entries:
        fname = os.path.basename(path)
        content = load_backup_content(path)
        snippet = json.dumps(content, indent=2)[:1000] if content else "(error loading file)"
        html += f'''
        <div class="log-entry">
            <strong>File:</strong> {fname}<br>
            <button onclick="window.location='/api/download-backup/{prefix}/{fname}'">⬇ Download</button>
            <button onclick="togglePreview(this)">👁 Preview</button>
            <button onclick="uploadBackup('{prefix}', '{fname}')">⏫ Use This Backup</button>
            <pre style="display:none;">{snippet}</pre>
        </div>
        '''
    html += f'''
        <div class="log-entry">
            <strong>Manual Backup:</strong><br>
            <button onclick="manualBackup('{prefix}')">💾 Create Manual Backup</button>
            <input type="file" onchange="uploadManual(event, '{prefix}')" />
        </div>
    '''
    return html

@debug_logs.route("/debug-logs", methods=["GET"])
def debug_logs_page():
    auth_header = request.headers.get("Authorization")
    if not check_auth(auth_header):
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login required"'})

    reward_logs = get_reward_logs()
    user_logs = load_json(USER_LOG_PATH, {})
    current_tasks = load_json(TASKS_PATH, {})
    focus_data = load_json(FOCUS_PATH, {})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Logs</title>
        <style>
            body {{
                font-family: Arial;
                background: #f8f8f8;
                padding: 20px;
                color: #222;
            }}
            h1 {{ color: #444; }}
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
                margin-top: 10px;
                background: #eee;
                padding: 10px;
                font-size: 13px;
                display: none;
            }}
        </style>
        <script>
            function showLogs(type) {{
                document.querySelectorAll(".log-type").forEach(el => el.style.display = "none");
                document.getElementById(type).style.display = "block";
                document.querySelectorAll(".nav button").forEach(btn => btn.classList.remove("active"));
                document.getElementById(type + "-btn").classList.add("active");
            }}
            function togglePreview(btn) {{
                const pre = btn.parentElement.querySelector("pre");
                pre.style.display = pre.style.display === "none" ? "block" : "none";
            }}
            function manualBackup(type) {{
                fetch(`/api/manual-backup/${{type}}`).then(() => location.reload());
            }}
            function uploadBackup(type, fname) {{
                fetch(`/api/restore-backup/${{type}}/${{fname}}`).then(() => alert("Backup restored."));
            }}
            function uploadManual(event, type) {{
                const file = event.target.files[0];
                const formData = new FormData();
                formData.append("file", file);
                fetch(`/api/upload-backup/${{type}}`, {{ method: "POST", body: formData }}).then(() => location.reload());
            }}
        </script>
    </head>
    <body>
        <h1>🛠 Debug Logs</h1>
        <div class="nav">
            <button id="rewards-btn" class="active" onclick="showLogs('rewards')">🎁 Coin Rewards</button>
            <button id="users-btn" onclick="showLogs('users')">👤 User Info</button>
            <button id="current-tasks-btn" onclick="showLogs('current-tasks')">📄 Current Tasks</button>
            <button id="focus-btn" onclick="showLogs('focus')">🌼 Focus Stats</button>
            <button id="tasks-btn" onclick="showLogs('tasks')">📝 Task Backups</button>
            <button id="coins-btn" onclick="showLogs('coins')">🪙 Coin Backups</button>
        </div>

        <div id="rewards" class="log-type">
            {''.join(f'''
            <div class="log-entry">
                <strong>User:</strong> {e.get('user_id')}<br>
                <strong>Task:</strong> {e.get('task_name')}<br>
                <strong>Difficulty:</strong> {e.get('difficulty')}<br>
                <strong>Coins:</strong> {e.get('coins')}<br>
                <strong>Timestamp:</strong> {e.get('timestamp')}
            </div>''' for e in reward_logs)}
        </div>

        <div id="users" class="log-type" style="display:none;">
            {''.join(f'''
            <div class="log-entry">
                <strong>User ID:</strong> {uid}<br>
                <strong>First Name:</strong> {info.get("first_name")}<br>
                <strong>Username:</strong> {info.get("username")}<br>
                <strong>Last Seen:</strong> {info.get("last_seen", "N/A")}
            </div>''' for uid, info in user_logs.items())}
        </div>

        <div id="current-tasks" class="log-type" style="display:none;">
            <div class="log-entry">
                <strong>File:</strong> user_tasks.json<br>
                <pre>{json.dumps(current_tasks, indent=2)[:2000]}</pre>
            </div>
        </div>

        <div id="focus" class="log-type" style="display:none;">
            {''.join(f'''
            <div class="log-entry">
                <strong>User ID:</strong> {uid}<br>
                <strong>Total Minutes:</strong> {d.get("total_minutes", 0)}<br>
                <strong>Sessions Completed:</strong> {d.get("sessions_completed", 0)}<br>
                <strong>Flowers Unlocked:</strong> {d.get("flowers_unlocked", 0)}<br>
                <ul>{''.join(f"<li>{k}: {v}</li>" for k, v in d.get("flowers", {}).items())}</ul>
            </div>''' for uid, d in focus_data.items())}
        </div>

        <div id="tasks" class="log-type" style="display:none;">
            {format_backup_html("tasks")}
        </div>

        <div id="coins" class="log-type" style="display:none;">
            {format_backup_html("coins")}
        </div>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")

@debug_logs.route("/api/download-backup/<btype>/<fname>")
def download_backup_file(btype, fname):
    path = os.path.join(BASE_DIR, "backups", fname)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)

@debug_logs.route("/api/manual-backup/<btype>")
def create_manual_backup(btype):
    file_path = get_file_path_for_type(btype)
    if not file_path:
        return "Invalid type", 400
    data = load_json(file_path, {})
    save_manual_backup(btype, file_path, data)
    return "Backup created", 200

@debug_logs.route("/api/restore-backup/<btype>/<fname>")
def restore_backup_file(btype, fname):
    file_path = get_file_path_for_type(btype)
    if not file_path:
        return "Invalid type", 400
    backup_path = os.path.join(BASE_DIR, "backups", fname)
    success = replace_data_file(file_path, backup_path)
    return ("Restored", 200) if success else ("Failed", 500)

@debug_logs.route("/api/upload-backup/<btype>", methods=["POST"])
def upload_manual_backup(btype):
    file = request.files.get("file")
    if not file:
        return "No file provided", 400

    file_path = get_file_path_for_type(btype)
    if not file_path:
        return "Invalid type", 400

    content = json.load(file)
    with open(file_path, "w") as f:
        json.dump(content, f, indent=2)

    save_manual_backup(btype, file_path, content)
    return "Uploaded and saved", 200
