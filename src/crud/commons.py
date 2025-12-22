from collections.abc import Sequence

from sqlalchemy import Select, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.movie import Movie, Star, Director, Genre
from src.schemas.interactions import LikeCreate, LikeResponse, LikeAction
from src.schemas.movie import SortOptions


def apply_filters(stmt: Select, params: "MovieQueryParameters") -> Select:
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


async def filter_movies(
        stmt: Select, params: "MovieQueryParameters", session: AsyncSession
) -> tuple[Sequence[Movie], int]:
    filtered_stmt = apply_filters(stmt, params)

    result_count = await session.execute(
        select(func.count()).select_from(filtered_stmt.subquery())
    )
    count = result_count.scalar() or 0

    data_stmt = (
        filtered_stmt
        .offset(params.offset)
        .limit(params.size)
        .options(
            joinedload(Movie.certification),
            selectinload(Movie.genres),
        )
    )

    result = await session.execute(data_stmt)
    movies = result.scalars().all()
    return movies, count


async def toggle_generic_like(
        entity_id: int,
        user_id: int,
        liked: LikeCreate,
        Model: type["MovieLike"] | type["CommentLike"],
        id_field_name: str,
        session: AsyncSession
) -> LikeResponse:
    id_column = getattr(Model, id_field_name)

    stmt = select(Model).where(
        id_column == entity_id, Model.user_id == user_id
    )
    result = await session.execute(stmt)
    like = result.scalar_one_or_none()
    if like:
        if like.like == liked.liked:
            await session.delete(like)
            action = LikeAction.DELETED
            state = None
        else:
            like.like = liked.liked
            action = LikeAction.UPDATED
            state = liked.liked
    else:
        spec_kwargs = {id_field_name: entity_id}
        like = Model(
            user_id=user_id,
            like=liked.liked,
            **spec_kwargs
        )
        session.add(like)
        action = LikeAction.CREATED
        state = liked.liked

    await session.commit()
    return LikeResponse(action=action, state=state)
