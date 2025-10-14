import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

async def transcribe_audio(audio_file_path: str) -> str:
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return transcript.get("text", "")
    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return ""
 
