import openai
import requests
import tempfile

from app.config import settings
from app.models.ai_result import AIResult
from app.models.db import Session, engine

openai.api_key = settings.OPENAI_API_KEY


def transcribe_audio(audio_url: str) -> str:
    """
    Download audio from URL and transcribe using Whisper.
    Returns raw transcript text.
    """
    print(f"[🎧] Downloading audio from: {audio_url}")
    response = requests.get(audio_url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(response.content)
        tmp.flush()

        print("[🔊] Sending audio to Whisper API...")
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=open(tmp.name, "rb"),
            response_format="text"
        )

    print("[✅] Transcription complete.")
    return transcript


def generate_summary(transcript: str) -> str:
    """
    Generate a GPT-based summary from the transcript.
    """
    print("[📝] Generating GPT summary...")
    prompt = f"Summarize the following call transcript in a few sentences:\n\n{transcript}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing call transcripts."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response.choices[0].message.content.strip()
    print("[✅] Summary generated.")
    return summary


def analyze_sentiment(transcript: str) -> str:
    """
    Simple sentiment classifier using GPT.
    Returns: Positive, Neutral, or Negative
    """
    print("[🔍] Analyzing sentiment...")
    sentiment_prompt = (
        f"Determine the sentiment of the following conversation (Positive, Neutral, Negative):\n\n{transcript}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are a sentiment analysis tool."},
            {"role": "user", "content": sentiment_prompt}
        ]
    )

    sentiment = response.choices[0].message.content.strip().lower()
    if "positive" in sentiment:
        return "Positive"
    elif "negative" in sentiment:
        return "Negative"
    else:
        return "Neutral"


def save_ai_result(call_id: int, transcript: str, summary: str, sentiment: str):
    """
    Save the AI result to the database.
    """
    with Session(engine) as session:
        ai_data = AIResult(
            call_id=call_id,
            transcript=transcript,
            summary=summary,
            sentiment=sentiment
        )
        session.add(ai_data)
        session.commit()
        print(f"[💾] AI result saved for Call ID: {call_id}")


def process_call(audio_url: str, call_id: int) -> dict:
    """
    Run full AI pipeline and store results in DB.
    """
    try:
        transcript = transcribe_audio(audio_url)
        summary = generate_summary(transcript)
        sentiment = analyze_sentiment(transcript)

        save_ai_result(call_id, transcript, summary, sentiment)

        return {
            "transcript": transcript,
            "summary": summary,
            "sentiment": sentiment
        }
    except Exception as e:
        print(f"[❌] Error during AI processing: {e}")
        return {
            "error": str(e)
        }
