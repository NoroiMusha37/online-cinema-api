from typing import TypeVar, Type

from fastapi import HTTPException
from sqlalchemy import and_, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from sqlalchemy.exc import IntegrityError

from src.models.movie import Movie, Genre, Certification, Star, Director
from src.schemas.moderator import MovieCreate, MovieUpdate, NamedEntity
from . import movie as movie_crud
from . import validation

T = TypeVar("T", Certification, Genre, Star, Director)


async def create_movie(
        movie_in: MovieCreate,
        session: AsyncSession,
) -> Movie:
    await validation.check_movie_exists(
        name=movie_in.name,
        year=movie_in.year,
        time=movie_in.time,
        session=session,
    )

    await validation.validate_certification(
        movie_in.certification_id, session
    )
    genres = await validation.validate_genres(movie_in.genre_ids, session)
    stars = await validation.validate_stars(movie_in.star_ids, session)
    directors = await validation.validate_directors(
        movie_in.director_ids, session
    )

    new_movie = Movie(
        **movie_in.model_dump(
            exclude={"genre_ids", "star_ids", "director_ids"}
        ),
        genres=genres,
        stars=stars,
        directors=directors
    )

    session.add(new_movie)
    await session.commit()
    return await movie_crud.get_movie_by_id(new_movie.id, session)


async def update_movie(
        movie_id: int,
        movie_in: MovieUpdate,
        session: AsyncSession,
) -> Movie:
    result = await session.execute(select(Movie).where(
        Movie.id == movie_id
    ).options(
        selectinload(Movie.genres),
        selectinload(Movie.stars),
        selectinload(Movie.directors),
    )
    )
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie not found.",
        )

    data = movie_in.model_dump(exclude_unset=True)

    await validation.check_movie_exists(
        name=data.get("name", movie.name),
        year=data.get("year", movie.year),
        time=data.get("time", movie.time),
        session=session,
        exclude_id=movie_id,
    )

    if "certification_id" in data:
        await validation.validate_certification(
            data["certification_id"], session
        )
    if "genre_ids" in data:
        movie.genres = await validation.validate_genres(
            data.pop("genre_ids"), session
        )
    if "star_ids" in data:
        movie.stars = await validation.validate_stars(
            data.pop("star_ids"), session
        )
    if "director_ids" in data:
        movie.directors = await validation.validate_directors(
            data.pop("director_ids"), session
        )

    for key, value in data.items():
        setattr(movie, key, value)
    await session.commit()
    return await movie_crud.get_movie_by_id(movie.id, session)


async def delete_movie(
        movie_id: int,
        session: AsyncSession,
) -> None:
    result = await session.execute(delete(Movie).where(
        Movie.id == movie_id
    ))
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found."
        )

    await session.commit()


async def create_named_entity(
        Model: Type[T],
        entity_in: NamedEntity,
        session: AsyncSession,
) -> T:
    result = await session.execute(select(Model).where(
        Model.name == entity_in.name
    ))
    entity = result.scalar_one_or_none()
    if entity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{Model.__name__} already exists.",
        )

    new_entity = Model(
        name=entity_in.name,
    )
    session.add(new_entity)
    await session.commit()
    await session.refresh(new_entity)
    return new_entity


async def update_named_entity(
        Model: Type[T],
        entity_id: int,
        entity_in: NamedEntity,
        session: AsyncSession,
) -> T:
    existing_entity = await session.execute(select(Model).where(
        and_(Model.name == entity_in.name, Model.id != entity_id)
    ))
    if existing_entity.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Name taken.",
        )

    result = await session.execute(select(Model).where(
        Model.id == entity_id
    ))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{Model.__name__} not found.",
        )

    entity.name = entity_in.name
    await session.commit()
    await session.refresh(entity)
    return entity


async def delete_named_entity(
        Model: Type[T],
        entity_id: int,
        session: AsyncSession,
) -> None:
    try:
        result = await session.execute(delete(Model).where(
            Model.id == entity_id
        ))
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{Model.__name__} not found.",
            )
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete {Model.__name__}. "
                   f"It is assigned to at least one movie",
        )
