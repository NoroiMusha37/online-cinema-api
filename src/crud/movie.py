import uuid
from typing import Tuple, Sequence

from sqlalchemy import Select, or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.movie import Movie, Director, Star, Genre, movie_genres
from src.schemas.movie import MovieQueryParameters, SortOptions


def apply_filters(stmt: Select, params: MovieQueryParameters) -> Select:
    if params.search:
        pattern = f"%{params.search}%"
        stmt = stmt.outerjoin(Movie.stars).outerjoin(Movie.directors)
        stmt = stmt.where(
            or_(
                Movie.name.ilike(pattern),
                Movie.description.ilike(pattern),
                Star.name.ilike(pattern),
                Director.name.ilike(pattern),
            )
        ).distinct()

    if params.genre_ids:
        stmt = (stmt.join(Movie.genres)
                .where(Genre.id.in_(params.genre_ids))
                .distinct()
                )
    if params.year_from:
        stmt = stmt.where(Movie.year >= params.year_from)
    if params.year_to:
        stmt = stmt.where(Movie.year <= params.year_to)
    if params.min_time:
        stmt = stmt.where(Movie.time >= params.min_time)
    if params.max_time:
        stmt = stmt.where(Movie.time <= params.max_time)
    if params.min_imdb:
        stmt = stmt.where(Movie.imdb >= params.min_imdb)
    if params.min_votes:
        stmt = stmt.where(Movie.votes >= params.min_votes)
    if params.min_meta_score:
        stmt = stmt.where(Movie.meta_score >= params.min_meta_score)
    if params.price_from:
        stmt = stmt.where(Movie.price >= params.price_from)
    if params.price_to:
        stmt = stmt.where(Movie.price <= params.price_to)

    sort_map = {
        SortOptions.YEAR_ASC: Movie.year.asc(),
        SortOptions.YEAR_DESC: Movie.year.desc(),
        SortOptions.TIME_ASC: Movie.time.asc(),
        SortOptions.TIME_DESC: Movie.time.desc(),
        SortOptions.IMDB_ASC: Movie.imdb.asc(),
        SortOptions.IMDB_DESC: Movie.imdb.desc(),
        SortOptions.VOTES_ASC: Movie.votes.asc(),
        SortOptions.VOTES_DESC: Movie.votes.desc(),
        SortOptions.META_SCORE_ASC: Movie.meta_score.asc(),
        SortOptions.META_SCORE_DESC: Movie.meta_score.desc(),
        SortOptions.GROSS_ASC: Movie.gross.asc(),
        SortOptions.GROSS_DESC: Movie.gross.desc(),
        SortOptions.PRICE_ASC: Movie.price.asc(),
        SortOptions.PRICE_DESC: Movie.price.desc(),
    }
    stmt = stmt.order_by(sort_map.get(params.sort_by, Movie.year.desc()))

    return stmt


async def get_movies(
        params: MovieQueryParameters, session: AsyncSession
) -> Tuple[Sequence[Movie], int]:
    stmt: Select = select(Movie)
    filtered_stmt = apply_filters(stmt, params)
    result_count = await session.execute(select(func.count())
                                         .select_from(filtered_stmt.subquery())
                                         )
    count = result_count.scalar_one()

    data_stmt = (
        filtered_stmt
        .offset(params.offset)
        .limit(params.size)
        .options(
            joinedload(Movie.certification),
            selectinload(Movie.genres)
        )
    )

    result = await session.execute(data_stmt)
    movies = result.scalars().all()

    return movies, count


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
            selectinload(Movie.stars),
            selectinload(Movie.directors),
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_genres_with_counts(session: AsyncSession):
    stmt = (
        select(
            Genre.id,
            Genre.name,
            func.count(movie_genres.c.genre_id).label("movie_count"),
        )
        .outerjoin(movie_genres, Genre.id == movie_genres.c.genre_id)
        .group_by(Genre.id)
        .order_by(Genre.name)
    )

    result = await session.execute(stmt)
    return result.all()
