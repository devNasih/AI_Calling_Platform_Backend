from app.services.dialers import make_twilio_call, make_callhippo_call
from app.models.call_log import CallLog, CallStatus
from app.models.db import engine
from sqlmodel import Session


def choose_provider(region: str = "global") -> str:
    """Select provider based on region."""
    return "callhippo" if region.lower() == "india" else "twilio"


async def make_outbound_call(
    name: str,
    number: str,
    message: str,
    region: str = "global",
    campaign_name: str = "Default"
):
    provider = choose_provider(region)
    status = CallStatus.initiated
    recording_url = None

    try:
        # ✅ Call the appropriate provider
        if provider == "callhippo":
            result = await make_callhippo_call(name, number, message)
        else:
            result = await make_twilio_call(name, number, message)

        if result.get("status") == "success":
            status = CallStatus.completed
            recording_url = result.get("recording_url")
        else:
            status = CallStatus.failed

    except Exception as e:
        print(f"[❌] Call error: {e}")
        status = CallStatus.failed

    # ✅ Log into DB
    with Session(engine) as session:
        call_log = CallLog(
            contact_name=name,
            contact_number=number,
            campaign_name=campaign_name,
            region=region,
            provider=provider,
            status=status,
            recording_url=recording_url
        )
        session.add(call_log)
        session.commit()
