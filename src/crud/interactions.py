from collections.abc import Sequence

from sqlalchemy import select, func, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.interactions import Comment, Rating, MovieLike, CommentLike
from src.models.movie import user_favorites
from src.schemas.interactions import (
    CommentCreate,
    RatingCreate,
    LikeCreate,
    LikeResponse,
)
from .commons import toggle_generic_like


async def toggle_movie_like(
    movie_id: int, user_id: int, liked: LikeCreate, session: AsyncSession
) -> LikeResponse:
    return await toggle_generic_like(
        entity_id=movie_id,
        user_id=user_id,
        liked=liked,
        Model=MovieLike,
        id_field_name="movie_id",
        session=session,
    )


async def create_comment(
    movie_id: int, user_id: int, comment: CommentCreate, session: AsyncSession
) -> Comment:
    new_comment = Comment(
        movie_id=movie_id,
        user_id=user_id,
        text=comment.text,
        parent_id=comment.parent_id,
    )

    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment


async def delete_comment(
    comment_id: int, user_id: int, session: AsyncSession
) -> bool:
    result = await session.execute(
        delete(Comment).where(
            Comment.id == comment_id, Comment.user_id == user_id
        )
    )

    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def get_comments_by_movie(
    movie_id: int, page: int, size: int, session: AsyncSession
) -> tuple[Sequence[Comment], int]:
    stmt = select(Comment).where(Comment.movie_id == movie_id)

    count = await session.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    count = count.scalar() or 0

    offset = (page - 1) * size
    stmt = stmt.order_by(Comment.created_at.desc()).offset(offset).limit(size)

    result = await session.execute(stmt)
    comments = result.scalars().all()
    return comments, count


async def upsert_rating(
    movie_id: int, user_id: int, rating_in: RatingCreate, session: AsyncSession
) -> Rating:
    stmt = select(Rating).where(
        Rating.user_id == user_id, Rating.movie_id == movie_id
    )
    result = await session.execute(stmt)
    rating = result.scalar_one_or_none()

    if rating:
        rating.score = rating_in.score
        await session.commit()
    else:
        rating = Rating(
            movie_id=movie_id,
            user_id=user_id,
            score=rating_in.score,
        )

        session.add(rating)

    await session.commit()
    await session.refresh(rating)
    return rating


async def toggle_favorite(
    movie_id: int, user_id: int, session: AsyncSession
) -> bool:
    stmt = delete(user_favorites).where(
        user_favorites.c.user_id == user_id,
        user_favorites.c.movie_id == movie_id,
    )

    result = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return False

    stmt = insert(user_favorites).values(user_id=user_id, movie_id=movie_id)
    await session.execute(stmt)
    await session.commit()
    return True


async def toggle_comment_like(
    comment_id: int, user_id: int, liked: LikeCreate, session: AsyncSession
) -> LikeResponse:
    return await toggle_generic_like(
        entity_id=comment_id,
        user_id=user_id,
        liked=liked,
        Model=CommentLike,
        id_field_name="comment_id",
        session=session,
    )
