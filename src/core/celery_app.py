from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.imports = [
    "src.tasks.email_tasks",
    "src.tasks.cleanup_tasks",
]

celery_app.conf.beat_schedule = {
    "cleanup-every-hour": {"task": "cleanup_expired_tokens", "schedule": 3600},
    "cancel-orders-every-hour": {
        "task": "cancel_pending_orders",
        "schedule": 3600,
    },
}
