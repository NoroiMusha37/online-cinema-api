from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.movie import Genre, Star, Director, Certification, Movie
from starlette import status


async def check_movie_exists(
        name: str | None,
        year: int | None,
        time: int | None,
        session: AsyncSession,
        exclude_id: int | None = None
):
    stmt = select(Movie).where(
        and_(Movie.name == name, Movie.year == year, Movie.time == time)
    )
    if exclude_id:
        stmt = stmt.where(Movie.id != exclude_id)

    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie already exists"
        )


async def validate_certification(
        certification_id: int, session: AsyncSession
) -> Certification:
    certification = (
        await session.execute(
            select(Certification).where(
                Certification.id == certification_id)
        )
    ).scalar_one_or_none()

    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found.",
        )

    return certification


async def validate_genres(
        genre_ids: list[int], session: AsyncSession
) -> list[Genre]:
    genres = list((
                      await session.execute(
                          select(Genre).where(Genre.id.in_(genre_ids))
                      )
                  ).scalars().all())
    if len(genres) != len(genre_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or more genres not found."
        )

    return genres


async def validate_stars(
        star_ids: list[int], session: AsyncSession
) -> list[Star]:
    stars = list((
                     await session.execute(
                         select(Star).where(Star.id.in_(star_ids))
                     )
                 ).scalars().all())
    if len(stars) != len(star_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or more stars not found."
        )

    return stars


async def validate_directors(
        director_ids: list[int], session: AsyncSession
) -> list[Director]:
    directors = list((
                         await session.execute(
                             select(Director).where(
                                 Director.id.in_(director_ids)
                             )
                         )
                     ).scalars().all())
    if len(directors) != len(director_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or more directors not found."
        )

    return directors
