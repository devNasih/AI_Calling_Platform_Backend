from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum


# ----------- AUTH -----------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# ----------- CONTACTS -----------

class ContactUpload(BaseModel):
    name: str
    phone_number: str


# ----------- CAMPAIGNS -----------

class CampaignRequest(BaseModel):
    campaign_name: str
    message: str  # Optional for fixed prompts; can expand later
    region: Optional[str] = "global"  # ✅ NEW: Enables Twilio vs CallHippo selection
    contact_list: List[ContactUpload]

class CampaignCreateRequest(BaseModel):
    name: str
    message: str
    region: str
    status: Optional[str] = "scheduled"

class CampaignScheduleRequest(BaseModel):
    name: str
    message: str
    region: str
    start_time: str  # ISO format: "2025-07-30T15:30:00"


# ----------- CALL EVENTS -----------

class CallWebhookRequest(BaseModel):
    call_sid: str
    from_number: str
    to_number: str
    status: Optional[str]
    recording_url: Optional[str] = None


# ----------- RESPONSES -----------

class SuccessResponse(BaseModel):
    message: str
