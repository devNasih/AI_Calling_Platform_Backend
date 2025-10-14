import requests
from twilio.rest import Client
from app.config import settings

# ------------------------------
# TWILIO CONFIG
# ------------------------------
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
TWILIO_CALLBACK_URL = settings.TWILIO_CALLBACK_URL  # From .env

# ------------------------------
# CALLHIPPO CONFIG
# ------------------------------
CALLHIPPO_API_KEY = settings.CALLHIPPO_API_KEY
CALLHIPPO_USER_ID = settings.CALLHIPPO_USER_ID
CALLHIPPO_AGENT_NUMBER = settings.CALLHIPPO_AGENT_NUMBER
CALLHIPPO_API_URL = "https://callhippo.com/api/v1/call/"


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


# ✅ CallHippo outbound call
async def make_callhippo_call(name: str, phone_number: str, message: str) -> dict:
    try:
        print(f"[CallHippo] Calling {phone_number} for {name}...")
        payload = {
            "user_id": CALLHIPPO_USER_ID,
            "to_number": phone_number,
            "from_number": CALLHIPPO_AGENT_NUMBER,
            "custom_message": message
        }
        headers = {
            "Authorization": f"Bearer {CALLHIPPO_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(CALLHIPPO_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "call_id": data.get("call_id"),
                "recording_url": data.get("recording_url")
            }
        else:
            return {"status": "failed", "error": response.text}
    except Exception as e:
        print(f"[❌ CallHippo Error]: {e}")
        return {"status": "failed", "error": str(e)}
 
