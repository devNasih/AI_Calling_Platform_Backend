from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import enum


class CampaignStatus(str, enum.Enum):
    scheduled = "scheduled"
    running = "running"
    paused = "paused"
    stopped = "stopped"
    completed = "completed"


class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    message: str
    region: str
    status: CampaignStatus = Field(default=CampaignStatus.scheduled)
    created_at: datetime = Field(default_factory=datetime.utcnow)
