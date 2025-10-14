from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.models.db import get_session
from app.models.call_log import CallLog

router = APIRouter()

@router.get("/history", response_model=List[CallLog])
def get_call_history(
    campaign_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """
    Fetch call logs with optional filters:
    - campaign_name
    - status (initiated, completed, failed)
    - region (global, india)
    - limit (default 50)
    """
    statement = select(CallLog).order_by(CallLog.timestamp.desc())

    # ✅ Apply filters dynamically
    if campaign_name:
        statement = statement.where(CallLog.campaign_name == campaign_name)
    if status:
        statement = statement.where(CallLog.status == status)
    if region:
        statement = statement.where(CallLog.region == region)

    # ✅ Limit results for performance
    results = session.exec(statement.limit(limit)).all()
    return results
