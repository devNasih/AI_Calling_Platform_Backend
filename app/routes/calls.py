from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import Response
from xml.etree.ElementTree import Element, tostring
from pydantic import BaseModel
from app.services.ai_pipeline import process_call
import uuid

# ✅ Single router instance
router = APIRouter()

# ✅ Store outbound messages temporarily (use Redis in production)
pending_outbound_messages = {}

# -----------------------------------
# POST /v1/calls/inbound — Twilio Webhook
# -----------------------------------
@router.post("/inbound")
async def handle_inbound_call(request: Request):
    """
    Handles inbound Twilio call.
    Responds with TwiML XML to instruct Twilio what to do.
    """
    form = await request.form()
    from_number = form.get("From", "")
    to_number = form.get("To", "")

    print(f"[Twilio Inbound] From: {from_number}, To: {to_number}")

    # ✅ Basic TwiML response (Future: AI-driven response)
    response = Element("Response")
    say = Element("Say", voice="alice")
    say.text = "Thank you for calling AI Calling Agent. Please wait while we connect you."
    response.append(say)

    xml_string = tostring(response, encoding='unicode')
    return Response(content=xml_string, media_type="application/xml")


# -----------------------------------
# GET/POST /v1/calls/outbound — Twilio Outbound Webhook
# -----------------------------------
@router.get("/outbound")
@router.post("/outbound")
async def handle_outbound_call(request: Request, message_id: str = Query(None)):
    """
    Handles outbound Twilio call webhook.
    Returns TwiML with the custom message for the call.
    """
    # Get parameters
    if request.method == "GET":
        params = request.query_params
    else:
        params = await request.form()
    
    call_sid = params.get("CallSid", "")
    if not message_id:
        message_id = params.get("message_id", "")
    
    print(f"[Twilio Outbound Callback] CallSid: {call_sid}, MessageID: {message_id}")
    
    # Retrieve the custom message
    message = pending_outbound_messages.get(message_id, "Hello! This is an automated call from our system.")
    
    # Clean up after retrieval
    if message_id in pending_outbound_messages:
        del pending_outbound_messages[message_id]
    
    # Create TwiML response
    response = Element("Response")
    say = Element("Say", voice="alice")
    say.text = message
    response.append(say)
    
    xml_string = tostring(response, encoding='unicode')
    return Response(content=xml_string, media_type="application/xml")


# -----------------------------------
# WebSocket: /v1/calls/live-transcription
# -----------------------------------
@router.websocket("/v1/calls/live-transcription")
async def live_transcription_socket(websocket: WebSocket):
    """
    Handles live transcription (MVP placeholder).
    Future: integrate Whisper STT streaming.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Simulate transcription response
            fake_response = f"Transcription: {data}"
            await websocket.send_text(fake_response)
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")


# -----------------------------------
# POST /v1/calls/process-ai — Run AI Pipeline
# -----------------------------------
class AICallRequest(BaseModel):
    call_id: int
    audio_url: str

@router.post("/process-ai")
def process_ai_result(payload: AICallRequest):
    """
    Trigger AI pipeline (transcription, summarization, sentiment) for a completed call.
    """
    if not payload.call_id or not payload.audio_url:
        raise HTTPException(status_code=400, detail="call_id and audio_url are required.")

    result = process_call(audio_url=payload.audio_url, call_id=payload.call_id)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "status": "processed",
        "call_id": payload.call_id,
        "ai_result": result
    }
# Export for use in other modules
__all__ = ['router', 'pending_outbound_messages']