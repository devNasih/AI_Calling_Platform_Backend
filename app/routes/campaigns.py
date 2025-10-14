from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from typing import List
from datetime import datetime
import logging

from app.jwt_auth import get_current_user
from app.models.schemas import CampaignRequest, SuccessResponse, CampaignScheduleRequest
from app.routes.contacts import contact_store
from app.services.dialer import make_outbound_call

from app.models.db import get_session
from app.models.campaign import Campaign, CampaignStatus
from app.tasks.campaign_tasks import run_campaign

logger = logging.getLogger(__name__)

router = APIRouter()

# -------------------------------
# POST /start — Run Campaign Now
# -------------------------------
@router.post("/start", response_model=SuccessResponse)
async def start_campaign(
    campaign: CampaignRequest,
    user: dict = Depends(get_current_user)
):
    if not contact_store:
        raise HTTPException(status_code=400, detail="No contacts uploaded.")

    successful_calls = 0
    failed_calls = 0

    for contact in contact_store:
        try:
            await make_outbound_call(
                name=contact.name,
                number=contact.phone_number,
                message=campaign.message,
                region=campaign.region,
                campaign_name=campaign.campaign_name
            )
            successful_calls += 1
        except Exception as e:
            print(f"[❌] Failed to call {contact.phone_number}: {e}")
            failed_calls += 1

    return {
        "message": f"Campaign '{campaign.campaign_name}' started. "
                   f"{successful_calls} call(s) initiated, {failed_calls} failed."
    }

# --------------------------------------
# POST /schedule — Schedule Campaign
# --------------------------------------

@router.post("/schedule")
def schedule_campaign(
    campaign_request: CampaignScheduleRequest,
    session: Session = Depends(get_session)
):
    try:
        run_at = datetime.fromisoformat(campaign_request.start_time)
    except ValueError as e:
        logger.error(f"Invalid datetime format: {e}")
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    # ✅ Create campaign in DB
    try:
        campaign = Campaign(
            name=campaign_request.name,
            message=campaign_request.message,
            region=campaign_request.region,
            status=CampaignStatus.scheduled
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
    except Exception as e:
        logger.error(f"Database error while creating campaign: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create campaign")

    # ✅ Schedule task via Celery
    try:
        run_campaign.apply_async(args=[campaign.id], eta=run_at)
    except Exception as e:
        logger.error(f"Failed to schedule Celery task: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule campaign task")

    return {
        "status": "scheduled",
        "campaign_id": campaign.id,
        "run_at": run_at.isoformat()
    }

# -----------------------------------------------------
# POST /control/{campaign_id}/{action} — Pause/Resume/Stop
# -----------------------------------------------------
@router.post("/control/{campaign_id}/{action}")
def control_campaign(
    campaign_id: int = Path(..., description="Campaign ID"),
    action: str = Path(..., regex="^(pause|resume|stop)$"),
    session: Session = Depends(get_session)
):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if action == "pause":
        if campaign.status != CampaignStatus.running:
            raise HTTPException(status_code=400, detail="Campaign not running")
        campaign.status = CampaignStatus.paused

    elif action == "resume":
        if campaign.status != CampaignStatus.paused:
            raise HTTPException(status_code=400, detail="Campaign not paused")
        campaign.status = CampaignStatus.running
        run_campaign.delay(campaign.id)  # resumes by re-triggering task

    elif action == "stop":
        if campaign.status in [CampaignStatus.stopped, CampaignStatus.completed]:
            raise HTTPException(status_code=400, detail="Campaign already ended")
        campaign.status = CampaignStatus.stopped

    session.add(campaign)
    session.commit()

    return {
        "status": "updated",
        "campaign_id": campaign.id,
        "new_status": campaign.status
    }
