from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select, delete, exists, func
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from src.models.cart import Cart, CartItem
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.movie import user_movies
from src.schemas.cart import CartCreate, CartItemCreate
from src.models import Movie


async def create_cart(cart_in: CartCreate, session: AsyncSession) -> Cart:
    result = await session.execute(
        select(Cart).where(Cart.user_id == cart_in.user_id)
    )
    old_cart = result.scalar_one_or_none()
    if old_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart already exists.",
        )

    new_cart = Cart(
        user_id=cart_in.user_id,
    )
    session.add(new_cart)
    await session.commit()
    await session.refresh(new_cart)
    return new_cart


async def get_cart_items(
    user_id: int, page: int, size: int, session: AsyncSession
) -> tuple[Sequence[CartItem], int]:
    count = await session.execute(
        select(func.count(CartItem.id))
        .join(Cart)
        .where(Cart.user_id == user_id)
    )
    count = count.scalar() or 0
    offset = (page - 1) * size

    stmt = (
        select(CartItem)
        .join(Cart)
        .options(joinedload(CartItem.movie).selectinload(Movie.genres))
        .where(Cart.user_id == user_id)
        .offset(offset)
        .limit(size)
    )

    cart_items = (await session.execute(stmt)).scalars().all()
    return cart_items, count


async def clear_cart(user_id: int, session: AsyncSession) -> None:
    stmt = delete(CartItem).where(
        CartItem.cart_id
        == select(Cart.id).where(Cart.user_id == user_id).scalar_subquery()
    )

    await session.execute(stmt)
    await session.commit()


async def create_cart_item(
    cart_item_in: CartItemCreate, user_id: int, session: AsyncSession
) -> CartItem | None:
    old_cart_item = await session.execute(
        select(CartItem)
        .join(Cart)
        .where(
            Cart.user_id == user_id, CartItem.movie_id == cart_item_in.movie_id
        )
    )
    if old_cart_item.scalar_one_or_none():
        return None

    purchased_item = await session.execute(
        select(
            exists().where(
                user_movies.c.user_id == user_id,
                user_movies.c.movie_id == cart_item_in.movie_id,
            )
        )
    )
    if purchased_item.scalar():
        return None

    movie = await session.execute(
        select(Movie)
        .where(Movie.id == cart_item_in.movie_id)
        .options(selectinload(Movie.genres))
    )
    movie = movie.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie doesn't exist.",
        )

    cart_result = await session.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = cart_result.scalar_one_or_none()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.flush()

    new_cart_item = CartItem(
        cart_id=cart.id, movie_id=cart_item_in.movie_id, movie=movie
    )
    session.add(new_cart_item)
    await session.commit()
    await session.refresh(new_cart_item, attribute_names=["id"])
    return new_cart_item


async def delete_cart_item(
    user_id: int, cart_item_id: int, session: AsyncSession
) -> None:
    stmt = delete(CartItem).where(
        CartItem.id == cart_item_id,
        CartItem.cart_id
        == (select(Cart.id).where(Cart.user_id == user_id).scalar_subquery()),
    )

    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such movie in the cart.",
        )

    await session.commit()
