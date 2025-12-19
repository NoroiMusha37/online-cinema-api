from typing import Tuple, Sequence

from sqlalchemy import and_, select, func, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.interactions import Like, Comment, Rating
from src.models.movie import user_favorites
from src.schemas.interactions import CommentCreate, RatingCreate, LikeCreate


async def upsert_like(
        movie_id: int,
        user_id: int,
        liked: LikeCreate,
        session: AsyncSession
) -> Like:
    stmt = select(Like).where(
        and_(Like.movie_id == movie_id, Like.user_id == user_id)
    )
    result = await session.execute(stmt)
    like = result.scalar_one_or_none()
    if like:
        like.like = liked.liked
    else:
        like = Like(
            movie_id=movie_id,
            user_id=user_id,
            like=liked.liked
        )
        session.add(like)

    await session.commit()
    await session.refresh(like)
    return like


async def delete_like(
        movie_id: int,
        user_id: int,
        session: AsyncSession
) -> None:
    await session.execute(delete(Like).where(
        and_(Like.movie_id == movie_id, Like.user_id == user_id)
    )
    )
    await session.commit()


async def create_comment(
        movie_id: int,
        user_id: int,
        comment: CommentCreate,
        session: AsyncSession
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
        comment_id: int,
        user_id: int,
        session: AsyncSession
) -> bool:
    result = await session.execute(delete(Comment).where(
        and_(Comment.id == comment_id, Comment.user_id == user_id)
    )
    )

    if result.rowcount > 0:
        await session.commit()
        return True

    return False


async def get_comments_by_movie(
        movie_id: int,
        page: int,
        size: int,
        session: AsyncSession
) -> Tuple[Sequence[Comment], int]:
    stmt = select(Comment).where(Comment.movie_id == movie_id)

    count = await session.execute(select(func.count())
                                  .select_from(stmt.subquery())
                                  )
    count = count.scalar_one()

    offset = (page - 1) * size
    stmt = (
        stmt
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    comments = result.scalars().all()
    return comments, count


async def upsert_rating(
        movie_id: int,
        user_id: int,
        rating_in: RatingCreate,
        session: AsyncSession
) -> Rating:
    stmt = select(Rating).where(
        and_(Rating.user_id == user_id, Rating.movie_id == movie_id)
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
        movie_id: int,
        user_id: int,
        session: AsyncSession
) -> bool:
    stmt = delete(user_favorites).where(
        and_(
            user_favorites.c.user_id == user_id,
            user_favorites.c.movie_id == movie_id
        )
    )

    result = await session.execute(stmt)
    if result.rowcount > 0:
        await session.commit()
        return False

    stmt = insert(user_favorites).values(
        user_id=user_id,
        movie_id=movie_id
    )
    await session.execute(stmt)
    await session.commit()
    return True
