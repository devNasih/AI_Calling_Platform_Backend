import time
import asyncio
from app.worker import celery_app
from app.services.dialer import make_outbound_call
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.db import engine
from sqlmodel import Session, select
from app.websockets.manager import manager

MAX_RETRIES = 3       # Maximum number of retries
RETRY_DELAY = 3       # Seconds to wait between retries

@celery_app.task(name="app.tasks.run_campaign")
def run_campaign(campaign_id: int):
    print(f"[🎯] Running campaign ID: {campaign_id}")

    with Session(engine) as session:
        campaign = session.get(Campaign, campaign_id)

        if not campaign:
            print(f"[❌] Campaign not found: ID {campaign_id}")
            return

        if campaign.status in [CampaignStatus.stopped, CampaignStatus.completed]:
            print(f"[🛑] Campaign ID {campaign_id} is not eligible to run.")
            return

        # ✅ Mark campaign as running
        campaign.status = CampaignStatus.running
        session.add(campaign)
        session.commit()

        contacts = session.exec(
            select(Contact).where(Contact.region == campaign.region)
        ).all()

        for contact in contacts:
            session.refresh(campaign)

            # ✅ Check for pause/stop before each call
            if campaign.status == CampaignStatus.paused:
                print(f"[⏸️] Campaign {campaign.id} paused. Exiting early.")
                asyncio.run(manager.broadcast(f"⏸️ Campaign {campaign.name} paused."))
                return
            if campaign.status == CampaignStatus.stopped:
                print(f"[🛑] Campaign {campaign.id} stopped. Exiting early.")
                asyncio.run(manager.broadcast(f"🛑 Campaign {campaign.name} stopped."))
                return

            retries = 0
            success = False

            while retries < MAX_RETRIES and not success:
                try:
                    make_outbound_call(
                        name=contact.name,
                        number=contact.phone_number,
                        message=campaign.message,
                        region=campaign.region,
                        campaign_name=campaign.name,
                    )
                    success = True
                    print(f"[✅] Call successful: {contact.phone_number}")
                    asyncio.run(manager.broadcast(
                        f"📞 Called {contact.name} ({contact.phone_number}) in campaign '{campaign.name}'"
                    ))
                except Exception as e:
                    retries += 1
                    print(f"[❌] Call failed ({retries}/{MAX_RETRIES}) for {contact.phone_number}: {e}")
                    if retries < MAX_RETRIES:
                        time.sleep(RETRY_DELAY)

            if not success:
                print(f"[🚫] All retries failed for {contact.phone_number}")
                asyncio.run(manager.broadcast(
                    f"🚫 Failed to call {contact.name} ({contact.phone_number}) after {MAX_RETRIES} retries"
                ))

        # ✅ Mark campaign as completed
        campaign.status = CampaignStatus.completed
        session.add(campaign)
        session.commit()
        print(f"[✅] Campaign ID {campaign.id} completed.")
        asyncio.run(manager.broadcast(f"✅ Campaign '{campaign.name}' completed."))
