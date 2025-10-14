from celery import Celery
from app.config import settings

# Create the Celery app
celery_app = Celery(
    "campaign_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "campaigns"}
}
 
