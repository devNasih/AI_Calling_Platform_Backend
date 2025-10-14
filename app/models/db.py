import os
from sqlmodel import SQLModel, create_engine, Session

from app.config import settings
from app.models.call_log import CallLog
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.models.ai_result import AIResult  # ✅ Add this

# ✅ Prefer DB_URL from .env if provided
if hasattr(settings, "DB_URL") and settings.DB_URL:
    DATABASE_URL = settings.DB_URL
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'calls.db')}"

# ✅ Engine
engine = create_engine(DATABASE_URL, echo=False)

# ✅ Create all tables
def init_db():
    SQLModel.metadata.create_all(engine)

# ✅ Session dependency
def get_session():
    with Session(engine) as session:
        yield session
