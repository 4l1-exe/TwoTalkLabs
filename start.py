import os
import sys
import subprocess
import socket
import time
import urllib.request
from pathlib import Path
from zipfile import ZipFile
import http.client
import webbrowser

# ----------------- Config ----------------- #
FFMPEG_DIR = Path(__file__).parent / "ffmpeg_bin"
FFMPEG_EXEC = FFMPEG_DIR / "bin" / "ffmpeg.exe" if os.name == "nt" else FFMPEG_DIR / "bin/ffmpeg"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
SERVER_MODULE = "server:app"

# ----------------- Utilities ----------------- #
def find_free_port(start=8000, end=8100):
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found between {start}-{end}")

def wait_for_server(port, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/")
            res = conn.getresponse()
            if res.status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

# ----------------- FFmpeg ----------------- #
def download_ffmpeg():
    if FFMPEG_EXEC.exists():
        print(f"✅ Bundled FFmpeg found at {FFMPEG_EXEC}")
        os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")
        return

    print("⬇️ FFmpeg not found, downloading...")

    FFMPEG_DIR.mkdir(exist_ok=True)
    zip_path = FFMPEG_DIR / "ffmpeg.zip"

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded / total_size * 100, 100)
        print(f"\rDownloading FFmpeg: {percent:.2f}% ({downloaded}/{total_size} bytes)", end="")

    urllib.request.urlretrieve(FFMPEG_URL, filename=zip_path, reporthook=progress_hook)
    print("\n✅ Download complete, extracting...")

    with ZipFile(zip_path, "r") as zip_ref:
        # Extract directly into FFMPEG_DIR
        for member in zip_ref.namelist():
            # Strip root folder if exists
            parts = Path(member).parts
            target = FFMPEG_DIR / Path(*parts[1:]) if len(parts) > 1 else FFMPEG_DIR / Path(*parts)
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, "wb") as f:
                    f.write(zip_ref.read(member))

    zip_path.unlink()
    os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ FFmpeg is ready at {FFMPEG_EXEC}")

# ----------------- Requirements ----------------- #
def install_requirements():
    print("🚀 Installing Python requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], check=True)
    print("✅ Requirements installed")

# ----------------- Start Server ----------------- #
def start_server(port):
    print(f"🌐 Starting server on port {port}...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", SERVER_MODULE, "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        text=True
    )

    # Stream logs in real-time
    while True:
        line = proc.stdout.readline()
        if line:
            print(line, end="")
        if wait_for_server(port, timeout=0.5):
            webbrowser.open(f"http://127.0.0.1:{port}")
            break

    # Wait for process to finish
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()

# ----------------- Main ----------------- #
if __name__ == "__main__":
    download_ffmpeg()
    install_requirements()
    port = find_free_port()
    start_server(port)
