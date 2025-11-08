from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from datetime import datetime
from core.groq_handler import generate_conversation
from core.elevenlabs_handler import synthesize_speech
from core.audio_merge import merge_audio
from core.utils import get_env, setup_folders
import shutil

# ---------------- Safe cleanup function ---------------- #
def cleanup_temp(temp_dir="assets/temp"):
    """
    Clear all files inside the specified temp directory but keep the folder itself.
    """
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(temp_dir, exist_ok=True)

# ---------------- FastAPI Setup ---------------- #
load_dotenv()  # Load environment variables from .env

app = FastAPI()
setup_folders()



# Serve frontend assets
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/generate")
async def generate(prompt: str = Form(...)):
    temp_dir = "assets/temp"
    output_dir = "assets/output"
    cleanup_temp(temp_dir)  # safely clear previous temp files
    os.makedirs(output_dir, exist_ok=True)

    # Generate conversation lines
    lines = generate_conversation(prompt)
    temp_files = []

    voice_a = get_env("ELEVEN_VOICE_ID_A")
    voice_b = get_env("ELEVEN_VOICE_ID_B")

    # Synthesize speech for each line
    for i, line in enumerate(lines):
        speaker = "A" if i % 2 == 0 else "B"
        voice = voice_a if speaker == "A" else voice_b
        temp_file = os.path.join(temp_dir, f"line_{i+1}_{speaker}.mp3")
        synthesize_speech(line, voice, temp_file)
        temp_files.append(temp_file)

    # Merge all audio files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_file = os.path.join(output_dir, f"final_conversation_{timestamp}.mp3")
    merge_audio(temp_files, final_file)

    # Optionally clean temp files again (safe)
    cleanup_temp(temp_dir)

    # Return the final MP3
    return HTMLResponse(open(final_file, "rb").read(), media_type="audio/mpeg")
