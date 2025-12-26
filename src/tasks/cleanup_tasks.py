from datetime import datetime, timezone, timedelta

from celery import shared_task
from sqlalchemy import delete, update

from src.core.database import SessionLocal
from src.models import ActivationToken, Order
from .commons import run_async_task
from ..models.order import OrderStatusEnum


async def cleanup():
    async with SessionLocal() as session:
        result = await session.execute(
            delete(ActivationToken)
            .where(ActivationToken.expires_at < datetime.now(timezone.utc))
        )

        await session.commit()
        print(f"Deleted {result.rowcount} expired ActivationTokens")


async def cancel_orders():
    async with SessionLocal() as session:
        threshold = datetime.now(timezone.utc) - timedelta(hours=24)

        stmt = (
            update(Order)
            .where(
                Order.created_at < threshold,
                Order.status == OrderStatusEnum.PENDING
            )
            .values(status=OrderStatusEnum.CANCELED)
        )
        result = await session.execute(stmt)

        await session.commit()
        print(f"Canceled {result.rowcount} pending orders")


@shared_task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    run_async_task(cleanup())


@shared_task(name="cancel_pending_orders")
def cancel_pending_orders():
    run_async_task(cancel_orders())
