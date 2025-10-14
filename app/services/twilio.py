from twilio.rest import Client
from app.config import settings

# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Twilio will fetch TwiML from this public endpoint during the call
TWIML_CALLBACK_URL = "https://your-public-ngrok-url.ngrok.io/v1/calls/inbound"  # Replace with your real callback

async def make_outbound_call(name: str, phone_number: str, message: str):
    print(f"[Twilio] Calling {phone_number} for {name}...")

    call = twilio_client.calls.create(
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        url=TWIML_CALLBACK_URL,  # Twilio will make a GET request to this URL
        method="GET"
    )

    print(f"[✔] Call initiated. SID: {call.sid}")
 
