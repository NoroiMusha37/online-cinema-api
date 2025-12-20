from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import delete

from src.core.database import SessionLocal
from src.models import ActivationToken
from .commons import run_async_task


async def cleanup():
    async with SessionLocal() as session:
        await session.execute(
            delete(ActivationToken)
            .where(ActivationToken.expires_at < datetime.now(timezone.utc))
        )

        await session.commit()


@shared_task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    run_async_task(cleanup())
