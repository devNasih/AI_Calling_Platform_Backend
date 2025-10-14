import requests
from app.config import settings

# Default voice settings (you can change to another voice_id later)
ELEVENLABS_VOICE_ID = "Rachel"  # Or replace with a real voice ID from your account
ELEVENLABS_API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

HEADERS = {
    "xi-api-key": settings.ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}

def synthesize_speech(text: str, output_path: str = "output.mp3"):
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.7
        }
    }

    try:
        response = requests.post(ELEVENLABS_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"[✔] Audio saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"[ELEVENLABS ERROR] {e}")
        return ""
 
