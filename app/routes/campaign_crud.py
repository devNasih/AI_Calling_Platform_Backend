from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
import logging
from datetime import datetime

from app.models.db import get_session
from app.models.campaign import Campaign, CampaignStatus
from app.models.schemas import CampaignCreateRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# ----------------------------
# Create a new campaign
# ----------------------------
@router.post("/", response_model=Campaign)
def create_campaign(campaign_request: CampaignCreateRequest, session: Session = Depends(get_session)):
    try:
        # Convert status string to enum
        status = CampaignStatus.scheduled
        if campaign_request.status:
            try:
                status = CampaignStatus(campaign_request.status)
            except ValueError:
                status = CampaignStatus.scheduled
        
        # Create Campaign object with proper datetime
        campaign = Campaign(
            name=campaign_request.name,
            message=campaign_request.message,
            region=campaign_request.region,
            status=status,
            created_at=datetime.utcnow()
        )
        
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        return campaign
    except Exception as e:
        logger.error(f"Database error while creating campaign: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create campaign")

# ----------------------------
# Get all campaigns
# ----------------------------
@router.get("/", response_model=List[Campaign])
def get_all_campaigns(session: Session = Depends(get_session)):
    statement = select(Campaign)
    return session.exec(statement).all()

# ----------------------------
# Get campaign by ID
# ----------------------------
@router.get("/{campaign_id}", response_model=Campaign)
def get_campaign_by_id(campaign_id: int, session: Session = Depends(get_session)):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

# ----------------------------
# Update a campaign
# ----------------------------
@router.put("/{campaign_id}", response_model=Campaign)
def update_campaign(campaign_id: int, updated: Campaign, session: Session = Depends(get_session)):
    existing = session.get(Campaign, campaign_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for field, value in updated.dict(exclude_unset=True).items():
        setattr(existing, field, value)

    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing

# ----------------------------
# Delete a campaign
# ----------------------------
@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, session: Session = Depends(get_session)):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    session.delete(campaign)
    session.commit()
    return {"message": "Campaign deleted successfully"}
