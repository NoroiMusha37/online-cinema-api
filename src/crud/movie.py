import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.movie import (
    Movie,
    Genre,
    movie_genres,
    user_favorites
)
from src.schemas.movie import MovieQueryParameters
from src.models.interactions import MovieLike, Comment, CommentLike, Rating
from .commons import filter_movies
from src.models.user import User


async def get_movies(
        params: MovieQueryParameters,
        session: AsyncSession,
        user_id: int | None = None
) -> tuple[Sequence[Movie], int]:
    stmt = select(Movie)
    if user_id:
        stmt = stmt.join(Movie.owners).where(User.id == user_id)
    return await filter_movies(stmt, params, session)


async def get_movie_by_uuid(
        movie_uuid: uuid.UUID, session: AsyncSession
) -> Movie | None:
    stmt = (
        select(Movie)
        .where(Movie.uuid == movie_uuid)
        .options(
            joinedload(Movie.certification),
            selectinload(Movie.genres),
            selectinload(Movie.stars),
            selectinload(Movie.directors),
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_movie_by_id(
        movie_id: int, session: AsyncSession
) -> Movie | None:
    stmt = (
        select(Movie)
        .where(Movie.id == movie_id)
        .options(
            joinedload(Movie.certification),
            selectinload(Movie.genres),
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_genres_with_counts(
        page: int,
        size: int,
        session: AsyncSession
):
    result_count = await session.execute(select(func.count(Genre.id)))
    count = result_count.scalar() or 0
    offset = (page - 1) * size

    stmt = (
        select(
            Genre.id,
            Genre.name,
            func.count(movie_genres.c.genre_id).label("movie_count"),
        )
        .outerjoin(movie_genres, Genre.id == movie_genres.c.genre_id)
        .group_by(Genre.id)
        .order_by(Genre.name)
        .offset(offset)
        .limit(size)
    )
    result = await session.execute(stmt)
    genres = result.mappings().all()

    return genres, count


async def get_user_favorites(
        user_id: int,
        params: MovieQueryParameters,
        session: AsyncSession
) -> tuple[Sequence[Movie], int]:
    stmt = (
        select(Movie)
        .join(user_favorites, Movie.id == user_favorites.c.movie_id)
        .where(user_favorites.c.user_id == user_id)
    )

    return await filter_movies(stmt, params, session)


async def get_user_liked_movies(
        user_id: int,
        liked: bool,
        params: MovieQueryParameters,
        session: AsyncSession
) -> tuple[Sequence[Movie], int]:
    stmt = (
        select(Movie)
        .join(MovieLike, Movie.id == MovieLike.movie_id)
        .where(
            MovieLike.user_id == user_id,
            MovieLike.like == liked
        )
    )

    return await filter_movies(stmt, params, session)


async def get_user_liked_comments(
        user_id: int,
        liked: bool,
        page: int,
        size: int,
        session: AsyncSession
) -> tuple[Sequence[Comment], int]:
    count = await session.execute(select(func.count()).where(
        CommentLike.user_id== user_id,
        CommentLike.like == liked
    )
    )
    count = count.scalar_one()

    offset = (page - 1) * size
    stmt = (
        select(Comment)
        .options(selectinload(Comment.movie))
        .join(CommentLike, Comment.id == CommentLike.comment_id)
        .where(
            CommentLike.user_id == user_id,
            CommentLike.like == liked
        )
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    comments = result.scalars().all()
    return comments, count


async def get_user_rated_movies(
        user_id: int,
        page: int,
        size: int,
        session: AsyncSession
) -> tuple[Sequence[Rating], int]:
    count = await session.execute(select(func.count())
                                  .select_from(Rating)
                                  .where(Rating.user_id == user_id)
                                  )
    count = count.scalar() or 0
    offset = (page - 1) * size

    stmt = (
        select(Rating)
        .options(
            joinedload(Rating.movie).options(
                joinedload(Movie.certification),
                selectinload(Movie.genres),
            )
        )
        .where(Rating.user_id == user_id)
        .order_by(Rating.score.desc())
        .offset(offset)
        .limit(size)
    )
    result = await session.execute(stmt)
    ratings = result.scalars().all()
    return ratings, count
