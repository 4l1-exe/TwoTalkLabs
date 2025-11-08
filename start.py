import subprocess
import sys
import os
import socket
import time
import webbrowser
from pathlib import Path
import urllib.request
import zipfile
import shutil

# ----------------- Settings ----------------- #
FFMPEG_DIR = Path(__file__).parent / "ffmpeg_bin"
FFMPEG_EXEC = FFMPEG_DIR / "bin" / "ffmpeg.exe"  # Path after extracting
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

# ----------------- Utility Functions ----------------- #
def find_free_port(start=8000, end=8100):
    for port in range(start, end+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found between {start}-{end}")

def run_command(cmd_list):
    subprocess.run(cmd_list, check=True)

# ----------------- FFmpeg Setup ----------------- #
def setup_ffmpeg():
    if FFMPEG_EXEC.exists():
        print("✅ Bundled FFmpeg found")
        os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")
        return

    print("⬇️ Downloading FFmpeg...")
    FFMPEG_DIR.mkdir(exist_ok=True)
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = FFMPEG_DIR / "ffmpeg.zip"

    # Download the zip
    urllib.request.urlretrieve(url, zip_path)

    # Extract zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        # Extract contents directly into ffmpeg_bin
        for member in zip_ref.namelist():
            # Skip root folder in zip
            parts = member.split('/')
            target = FFMPEG_DIR / '/'.join(parts[1:])
            if member.endswith('/'):
                target.mkdir(parents=True, exist_ok=True)
            else:
                with open(target, "wb") as f:
                    f.write(zip_ref.read(member))

    zip_path.unlink()
    os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")
    print("✅ FFmpeg setup complete")

# ----------------- Install Requirements ----------------- #
def install_requirements():
    if REQUIREMENTS_FILE.exists():
        print("🚀 Installing Python packages...")
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
        print("✅ Python packages installed")

# ----------------- Wait for Server ----------------- #
def wait_for_server(host="127.0.0.1", port=8000, timeout=10):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            if time.time() - start_time > timeout:
                raise RuntimeError("Server failed to start in time")
            time.sleep(0.2)

# ----------------- Main Routine ----------------- #
def main():
    install_requirements()
    setup_ffmpeg()
    port = find_free_port()
    print(f"Starting server on port {port}...")

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app",
         "--host", "127.0.0.1",
         "--port", str(port),
         "--reload"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        wait_for_server(port=port)
        url = f"http://127.0.0.1:{port}"
        print(f"✅ Server is ready at {url}")
        webbrowser.open(url)
        proc.wait()
    finally:
        proc.terminate()
        print("Server process terminated.")

if __name__ == "__main__":
    main()
