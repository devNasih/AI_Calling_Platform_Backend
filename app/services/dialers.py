import requests
from twilio.rest import Client
from app.config import settings
from app.routes.calls import pending_outbound_messages
import uuid

# ------------------------------
# TWILIO CONFIG
# ------------------------------
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
TWILIO_CALLBACK_URL = settings.TWILIO_CALLBACK_URL  # From .env



# ✅ Twilio outbound call
async def make_twilio_call(name: str, phone_number: str, message: str) -> dict:
    try:
        print(f"[Twilio] Calling {phone_number} for {name}...")
        
        # Generate unique ID for this call
        message_id = str(uuid.uuid4())
        
        # Store message temporarily
        pending_outbound_messages[message_id] = message
        
        # Build callback URL with message_id
        callback_url = f"https://ai-calling.duckdns.org/v1/calls/outbound?message_id={message_id}"
        
        call = twilio_client.calls.create(
            to=phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=callback_url,
            method="GET"
        )
        
        return {"status": "success", "sid": call.sid, "recording_url": None}
    except Exception as e:
        print(f"[❌ Twilio Error]: {e}")
        return {"status": "failed", "error": str(e)}