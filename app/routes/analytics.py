from fastapi import APIRouter
from sqlmodel import Session, select, func
from collections import Counter

from app.models.db import engine
from app.models.call_log import CallLog
from app.models.ai_result import AIResult
from app.models.campaign import Campaign
from app.models.contact import Contact

router = APIRouter()

@router.get("/summary")
def get_platform_summary():
    with Session(engine) as session:
        # Total Calls
        total_calls = session.exec(select(func.count()).select_from(CallLog)).one()

        # Success / Failure
        calls = session.exec(select(CallLog)).all()
        success_count = len([c for c in calls if c.status == "completed"])
        failed_count = len([c for c in calls if c.status != "completed"])

        # Sentiment analysis
        sentiments = session.exec(select(AIResult.sentiment)).all()
        sentiment_counter = Counter(sentiments)

        return {
            "total_calls": total_calls,
            "successful_calls": success_count,
            "failed_calls": failed_count,
            "sentiment_distribution": {
                "positive": sentiment_counter.get("Positive", 0),
                "neutral": sentiment_counter.get("Neutral", 0),
                "negative": sentiment_counter.get("Negative", 0)
            },
            "ai_processed_calls": len(sentiments)
        }

@router.get("/campaign-stats")
def campaign_statistics():
    with Session(engine) as session:
        logs = session.exec(select(CallLog)).all()

        campaign_data = {}
        for log in logs:
            campaign = log.campaign_name or "Unassigned"
            campaign_data.setdefault(campaign, {"total": 0, "success": 0, "failed": 0})
            campaign_data[campaign]["total"] += 1
            if log.status == "completed":
                campaign_data[campaign]["success"] += 1
            else:
                campaign_data[campaign]["failed"] += 1

        return campaign_data
