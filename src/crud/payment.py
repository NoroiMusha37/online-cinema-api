from collections.abc import Sequence
from datetime import datetime, timezone, timedelta

import stripe
from fastapi import HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload, joinedload
from starlette import status

from src.models import Payment, PaymentItem, OrderItem
from src.models.movie import user_movies
from src.models.order import OrderStatusEnum
from src.models.payment import PaymentStatusEnum
from src.schemas.payment import PaymentCreate
from src.crud import order as order_crud


async def get_payment_by_id(payment_id: int, session: AsyncSession) -> Payment:
    stmt = (
        select(Payment)
        .options(
            selectinload(Payment.payment_items)
            .joinedload(PaymentItem.order_item)
            .joinedload(OrderItem.movie)
        )
        .where(Payment.id == payment_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_payments(
    user_id: int, page: int, size: int, session: AsyncSession
) -> tuple[Sequence[Payment], int]:
    count = await session.execute(
        select(func.count(Payment.id)).where(Payment.user_id == user_id)
    )
    count = count.scalar() or 0
    offset = (page - 1) * size

    stmt = (
        select(Payment)
        .options(
            selectinload(Payment.payment_items)
            .joinedload(PaymentItem.order_item)
            .joinedload(OrderItem.movie)
        )
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    payments = result.scalars().all()
    return payments, count


async def get_all_payments(
    page: int,
    size: int,
    session: AsyncSession,
    user_id: int | None = None,
    start_date: int | None = None,
    end_date: int | None = None,
    status: PaymentStatusEnum | None = None,
) -> tuple[Sequence[Payment], int]:
    count_stmt = select(func.count(Payment.id))
    stmt = select(Payment).options(
        selectinload(Payment.payment_items)
        .joinedload(PaymentItem.order_item)
        .joinedload(OrderItem.movie)
    )

    filters = []
    if user_id:
        filters.append(Payment.user_id == user_id)
    if start_date:
        filters.append(Payment.created_at >= start_date)
    if end_date:
        filters.append(Payment.created_at <= end_date)
    if status:
        filters.append(Payment.status == status)

    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)

    count_result = await session.execute(count_stmt)
    count = count_result.scalar() or 0
    offset = (page - 1) * size

    stmt = stmt.order_by(Payment.created_at.desc()).offset(offset).limit(size)

    result = await session.execute(stmt)
    payments = result.scalars().all()

    return payments, count


async def create_payment(
    payment_in: PaymentCreate,
    session: AsyncSession,
) -> Payment:
    order = await order_crud.get_order_by_id(
        order_id=payment_in.order_id,
        user_id=payment_in.user_id,
        session=session,
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    new_payment = Payment(
        user_id=payment_in.user_id,
        order_id=payment_in.order_id,
        amount=payment_in.amount,
        external_payment_id=payment_in.external_payment_id,
        status=payment_in.status,
    )
    session.add(new_payment)
    await session.flush()

    if payment_in.status == PaymentStatusEnum.SUCCESSFUL:
        purchased_movies = []
        for item in order.items:
            session.add(
                PaymentItem(
                    payment_id=new_payment.id,
                    order_item_id=item.id,
                    price_at_payment=item.price_at_order,
                )
            )

            purchased_movies.append(
                {
                    "user_id": payment_in.user_id,
                    "movie_id": item.movie_id,
                }
            )

        if purchased_movies:
            await session.execute(
                pg_insert(user_movies)
                .values(purchased_movies)
                .on_conflict_do_nothing()
            )
        order.status = OrderStatusEnum.PAID

    else:
        order.status = OrderStatusEnum.CANCELED

    await session.commit()

    final_stmt = (
        select(Payment)
        .options(
            joinedload(Payment.user),
            selectinload(Payment.payment_items)
            .joinedload(PaymentItem.order_item)
            .joinedload(OrderItem.movie),
        )
        .where(Payment.id == new_payment.id)
    )
    final_result = await session.execute(final_stmt)
    return final_result.scalar_one()


async def process_refund(
    user_id: int,
    payment_id: int,
    session: AsyncSession,
) -> Payment:
    stmt = (
        select(Payment)
        .options(
            selectinload(Payment.payment_items)
            .joinedload(PaymentItem.order_item)
            .joinedload(OrderItem.movie),
            joinedload(Payment.order),
        )
        .where(
            Payment.user_id == user_id,
            Payment.id == payment_id,
        )
    )
    result = await session.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    if datetime.now(timezone.utc) - payment.created_at > timedelta(hours=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund period expired.",
        )

    refunded_payments = await session.execute(
        select(func.count(Payment.id)).where(
            Payment.order_id == payment.order_id,
            Payment.status == PaymentStatusEnum.REFUNDED,
        )
    )
    if refunded_payments.scalar_one() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been refunded.",
        )

    try:
        stripe.Refund.create(payment_intent=payment.external_payment_id)

        refund = Payment(
            user_id=user_id,
            order_id=payment.order_id,
            amount=-payment.amount,
            external_payment_id=payment.external_payment_id,
            status=PaymentStatusEnum.REFUNDED,
        )
        session.add(refund)
        await session.flush()

        movie_ids = []
        for item in payment.payment_items:
            session.add(
                PaymentItem(
                    payment_id=refund.id,
                    order_item_id=item.order_item_id,
                    price_at_payment=-item.price_at_payment,
                )
            )
            movie_ids.append(item.order_item.movie_id)

        await session.execute(
            delete(user_movies).where(
                user_movies.c.user_id == user_id,
                user_movies.c.movie_id.in_(movie_ids),
            )
        )
        payment.order.status = OrderStatusEnum.CANCELED

        await session.commit()
        final_stmt = (
            select(Payment)
            .options(
                joinedload(Payment.user),
                selectinload(Payment.payment_items)
                .joinedload(PaymentItem.order_item)
                .joinedload(OrderItem.movie),
            )
            .where(Payment.id == refund.id)
        )
        final_result = await session.execute(final_stmt)
        return final_result.scalar_one()

    except stripe.error.StripeError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}",
        )
