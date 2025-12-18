from datetime import datetime, timezone
import asyncio

from celery import shared_task
from sqlalchemy import delete

from src.core.database import SessionLocal
from src.models.user import ActivationToken


async def cleanup():
    async with SessionLocal() as session:
        await session.execute(
            delete(ActivationToken)
            .where(ActivationToken.expires_at < datetime.now(timezone.utc))
        )

        await session.commit()


@shared_task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cleanup())
