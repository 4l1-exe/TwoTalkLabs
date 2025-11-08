import requests
from core.utils import get_env

def synthesize_speech(text: str, voice_id: str, output_path: str):
    """Generate audio from text using ElevenLabs API."""
    api_key = get_env("ELEVENLABS_API_KEY")

    # ✅ Auto-fix if user mistakenly puts a URL instead of ID
    if "voiceId=" in voice_id:
        voice_id = voice_id.split("voiceId=")[-1]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        print(f"[ElevenLabs Error] {res.status_code}: {res.text}")
    res.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(res.content)
