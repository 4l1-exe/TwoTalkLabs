import os
import shutil
import time
from pathlib import Path

def setup_folders():
    """Ensure temp/ and output/ folders exist inside assets/."""
    os.makedirs("assets/temp", exist_ok=True)
    os.makedirs("assets/output", exist_ok=True)


def cleanup_temp(temp_dir="assets/temp", retries: int = 5, delay: float = 0.1):
    """
    Safely delete temp_dir and all its contents.
    On Windows, retries if files are locked.
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return

    for attempt in range(retries):
        try:
            shutil.rmtree(temp_path)
            break
        except PermissionError:
            time.sleep(delay)

    # Final attempt: delete individual files
    for f in temp_path.glob("*"):
        try:
            f.unlink()
        except PermissionError:
            pass
    try:
        temp_path.rmdir()
    except Exception:
        pass


def get_env(var_name, default=None):
    """Get environment variable safely."""
    value = os.environ.get(var_name)
    if value is not None:
        return value

    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{var_name}="):
                    return line.split("=", 1)[1].strip()

    if default is not None:
        return default
    raise EnvironmentError(f"Missing environment variable: {var_name}")
