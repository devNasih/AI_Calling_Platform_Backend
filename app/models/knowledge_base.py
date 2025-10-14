from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class KnowledgeBaseFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    filepath: str
    filetype: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
