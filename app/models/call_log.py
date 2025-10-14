from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    initiated = "initiated"
    completed = "completed"
    failed = "failed"


class CallLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contact_name: str = Field(index=True)
    contact_number: str = Field(index=True)
    campaign_name: str = Field(index=True)
    region: str
    provider: str
    status: CallStatus = Field(default=CallStatus.initiated)
    recording_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds, future use
    ai_summary: Optional[str] = None  # Future AI call summary
    timestamp: datetime = Field(default_factory=datetime.utcnow)
