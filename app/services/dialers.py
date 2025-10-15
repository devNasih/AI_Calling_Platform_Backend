import requests
from twilio.rest import Client
from app.config import settings

# ------------------------------
# TWILIO CONFIG
# ------------------------------
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
TWILIO_CALLBACK_URL = settings.TWILIO_CALLBACK_URL  # From .env



# ✅ Twilio outbound call
async def make_twilio_call(name: str, phone_number: str, message: str) -> dict:
    try:
        print(f"[Twilio] Calling {phone_number} for {name}...")
        call = twilio_client.calls.create(
            to=phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=TWILIO_CALLBACK_URL,  # Twilio will GET this URL
            method="GET"
        )
        return {"status": "success", "sid": call.sid, "recording_url": None}
    except Exception as e:
        print(f"[❌ Twilio Error]: {e}")
        return {"status": "failed", "error": str(e)}