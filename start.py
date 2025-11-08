import os
import sys
import zipfile
import urllib.request
from pathlib import Path
import platform
import subprocess
import socket
import webbrowser
import time

# ----------------- FFmpeg Setup ----------------- #
FFMPEG_DIR = Path(__file__).parent / "ffmpeg_bin"
FFMPEG_EXEC = FFMPEG_DIR / "bin" / ("ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")

def ensure_ffmpeg():
    if FFMPEG_EXEC.exists():
        print("✅ FFmpeg found.")
    else:
        print("⬇️ FFmpeg not found. Downloading...")
        FFMPEG_DIR.mkdir(exist_ok=True)
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = FFMPEG_DIR / "ffmpeg.zip"

        # Download FFmpeg
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("✅ Download complete. Extracting...")

        # Extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(FFMPEG_DIR)
        zip_path.unlink()
        print("✅ FFmpeg extracted.")

    # Add to PATH for this session
    os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")

ensure_ffmpeg()

# ----------------- Find Free Port ----------------- #
def find_free_port(start=8000, end=8100):
    for port in range(start, end+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found between {start}-{end}")

port = find_free_port()
print(f"Starting server on localhost:{port}...")

# ----------------- Start Uvicorn ----------------- #
server_process = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "server:app",
    "--host", "localhost",
    "--port", str(port),
    "--reload"
], cwd=os.path.dirname(os.path.abspath(__file__)))

# ----------------- Open Browser ----------------- #
time.sleep(2)  # give server time to start
url = f"http://localhost:{port}"
print(f"🌐 Opening browser at {url}...")
webbrowser.open(url)

# Wait for the server to exit
try:
    server_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down server...")
    server_process.terminate()
