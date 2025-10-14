from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class AIResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    call_id: int  # Foreign key ref to CallLog.id
    transcript: str
    summary: str
    sentiment: str  # e.g., "Positive", "Negative", "Neutral"
    created_at: datetime = Field(default_factory=datetime.utcnow)
