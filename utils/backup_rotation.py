import os
import glob


def rotate_backups(directory: str, pattern: str, max_files: int = 5) -> None:
    """Keep only the newest backup files matching the pattern."""
    files = sorted(
        glob.glob(os.path.join(directory, pattern))
    )
    if len(files) <= max_files:
        return
    old_files = files[:-max_files]
    for path in old_files:
        try:
            os.remove(path)
            print(f"[INFO] Deleted old backup: {path}")
        except OSError as e:
            print(f"[ERROR] Failed to delete {path}: {e}")
