from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class KnowledgeChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="knowledgebasefile.id")
    chunk_text: str
    embedding: bytes  # Store as binary blob (can also use ARRAY if using Postgres)
    created_at: datetime = Field(default_factory=datetime.utcnow)
