import os
import json
import glob
import datetime

# ───── Base paths ───── #
BASE_DIR = "/mnt/data"
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

TASKS_FILE = os.path.join(BASE_DIR, "data/user_tasks.json")
COINS_FILE = os.path.join(BASE_DIR, "data/user_coins.json")

def ensure_backup_dir():
    """Ensure backup directory exists."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def save_manual_backup(prefix, target_path, data):
    """Create and save a manual backup file with timestamp."""
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_backup_{timestamp}.json"
    full_path = os.path.join(BACKUP_DIR, filename)
    with open(full_path, "w") as f:
        json.dump(data, f, indent=2)
    return filename

def list_backups(prefix):
    """List recent backup files matching the prefix."""
    pattern = os.path.join(BACKUP_DIR, f"{prefix}_backup_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    return files[:5]

def load_backup_content(path):
    """Load the content of a backup JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

def replace_data_file(target_file, backup_path):
    """Overwrite the main file with content from a backup."""
    try:
        with open(backup_path, "r") as f:
            data = json.load(f)
        with open(target_file, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def get_file_path_for_type(btype):
    """Return the correct file path for a given backup type."""
    if btype == "tasks":
        return TASKS_FILE
    elif btype == "coins":
        return COINS_FILE
    else:
        return None
