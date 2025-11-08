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
FFMPEG_EXEC = FFMPEG_DIR / "bin" / "ffmpeg.exe" if os.name == "nt" else FFMPEG_DIR / "bin" / "ffmpeg"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
SERVER_MODULE = "server:app"
HOST = "127.0.0.1"
PORT = 8017

# ----------------- Utilities ----------------- #
def find_free_port(port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, port))
            return port
        except OSError:
            raise RuntimeError(f"Port {port} is in use.")

def wait_for_server(port, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection(HOST, port, timeout=1)
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
        print(f"✅ FFmpeg already exists at {FFMPEG_EXEC}")
        os.environ["PATH"] = str(FFMPEG_DIR / "bin") + os.pathsep + os.environ.get("PATH", "")
        return

    print("⬇️ FFmpeg not found, downloading...")

    FFMPEG_DIR.mkdir(exist_ok=True)
    zip_path = FFMPEG_DIR / "ffmpeg.zip"

    def progress_hook(block_num, block_size, total_size):
        downloaded_mb = block_num * block_size / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        percent = min(downloaded_mb / total_mb * 100, 100)
        print(f"\rDownloading FFmpeg: {percent:.2f}% ({downloaded_mb:.2f}/{total_mb:.2f} MB)", end="")

    urllib.request.urlretrieve(FFMPEG_URL, filename=zip_path, reporthook=progress_hook)
    print("\n✅ Download complete, extracting...")

    with ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
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
def start_server():
    print(f"🌐 Starting server on http://{HOST}:{PORT} ...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", SERVER_MODULE, "--host", HOST, "--port", str(PORT), "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        text=True
    )

    # Stream logs and open browser when server is ready
    opened = False
    while True:
        line = proc.stdout.readline()
        if line:
            print(line, end="")
            if not opened and f"Uvicorn running on http://{HOST}:{PORT}" in line:
                webbrowser.open(f"http://{HOST}:{PORT}")
                opened = True

        # Exit if process ends
        if proc.poll() is not None:
            break

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()

# ----------------- Main ----------------- #
if __name__ == "__main__":
    download_ffmpeg()
    install_requirements()
    start_server()
