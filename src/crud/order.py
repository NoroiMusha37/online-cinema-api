from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.models import Cart, CartItem
from src.models.movie import user_movies, Movie
from src.models.order import Order, OrderItem, StatusEnum
from src.schemas.order import OrderUpdate
from src.crud import cart as cart_crud


async def get_order_by_id(
        order_id: int,
        user_id: int,
        session: AsyncSession
) -> Order | None:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items)
            .joinedload(OrderItem.movie)
        )
        .where(
            Order.id == order_id,
            Order.user_id == user_id
        )
    )

    order = await session.execute(stmt)
    return order.scalar_one_or_none()


async def get_user_orders(
        user_id: int,
        page: int,
        size: int,
        session: AsyncSession
) -> tuple[Sequence[Order], int]:
    count = await session.execute(
        select(
            func.count(Order.id))
        .where(Order.user_id == user_id)
    )
    count = count.scalar() or 0
    offset = (page - 1) * size

    stmt = (
        select(Order)
        .options(
            selectinload(Order.items)
            .joinedload(OrderItem.movie)
        )
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    orders = result.scalars().all()
    return orders, count


async def get_all_orders(
        page: int,
        size: int,
        session: AsyncSession,
        user_id: int | None = None,
        status: StatusEnum | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
) -> tuple[Sequence[Order], int]:
    count_stmt = select(func.count(Order.id))
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items)
            .joinedload(OrderItem.movie)
        )
    )

    filters = []
    if user_id:
        filters.append(Order.user_id == user_id)
    if status:
        filters.append(Order.status == status)
    if start_date:
        filters.append(Order.created_at >= start_date)
    if end_date:
        filters.append(Order.created_at <= end_date)

    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)

    count_result = await session.execute(count_stmt)
    count = count_result.scalar() or 0
    offset = (page - 1) * size
    stmt = (
        stmt
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    orders = result.scalars().all()

    return orders, count


async def create_order(
        user_id: int,
        total_amount: Decimal,
        items_data: list[dict],
        session: AsyncSession,
) -> Order:
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount
    )
    session.add(new_order)
    await session.flush()

    for item in items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            movie_id=item["movie_id"],
            price_at_order=item["price"],
        )
        session.add(order_item)

    await session.commit()
    await session.refresh(new_order, attribute_names=["items"])
    return new_order


async def checkout_cart(
        user_id: int,
        session: AsyncSession,
):
    cart_stmt = (
        select(Cart)
        .options(
            selectinload(Cart.cart_items)
            .joinedload(CartItem.movie)
            .selectinload(Movie.genres)
        )
        .where(Cart.user_id == user_id)
    )
    cart_result = await session.execute(cart_stmt)
    cart = cart_result.scalar_one_or_none()

    if not cart or not cart.cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The cart is empty."
        )

    purchased_stmt = (
        select(user_movies.c.movie_id)
        .where(user_movies.c.user_id == user_id)
    )
    purchased_result = await session.execute(purchased_stmt)
    purchased_ids = set(purchased_result.scalars().all())

    movies_to_checkout = []
    total_amount = Decimal(0)

    for cart_item in cart.cart_items:
        movie = cart_item.movie

        if not movie or movie.id in purchased_ids:
            continue

        movies_to_checkout.append({
            "movie_id": movie.id,
            "price": movie.price,
        })
        total_amount += movie.price

    if not movies_to_checkout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All movies are either already purchased "
                   "or not available."
        )

    new_order = await create_order(
        user_id=user_id,
        total_amount=total_amount,
        items_data=movies_to_checkout,
        session=session
    )
    await cart_crud.clear_cart(
        user_id=user_id,
        session=session
    )

    await session.refresh(new_order, attribute_names=["items"])
    return new_order


async def update_order(
        order_id: int,
        order_in: OrderUpdate,
        session: AsyncSession,
        user_id: int | None = None
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items)
            .joinedload(OrderItem.movie)
        )
        .where(Order.id == order_id)
    )

    if user_id:
        stmt = stmt.where(Order.user_id == user_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    if user_id:
        if order_in.status == StatusEnum.CANCELED:
            if order.status != StatusEnum.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You can cancel only pending orders.",
                )
            order.status = StatusEnum.CANCELED
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only set pending orders to cancelled.",
            )
    else:
        order.status = order_in.status

    await session.commit()
    await session.refresh(order)
    return order
