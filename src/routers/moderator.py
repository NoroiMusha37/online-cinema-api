from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_moderator
from src.models.movie import Genre, Star, Director, Certification
from src.schemas.moderator import MovieCreate, MovieUpdate, NamedEntity, NamedEntityResponse
from src.schemas.movie import MovieDetail
from src.crud import moderator as moder_crud

router = APIRouter(
    prefix="/moderator",
    dependencies=[Depends(get_current_moderator)]
)


@router.post("/movies", response_model=MovieDetail)
async def create_movie(
        movie_in: MovieCreate,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_movie(
        movie_in=movie_in,
        session=session,
    )


@router.patch("/movies/{movie_id}", response_model=MovieDetail)
async def update_movie(
        movie_id: int,
        movie_in: MovieUpdate,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_movie(
        movie_id=movie_id,
        movie_in=movie_in,
        session=session,
    )


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
        movie_id: int,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.delete_movie(
        movie_id=movie_id,
        session=session,
    )


@router.post("/genres", response_model=NamedEntityResponse)
async def create_genre(
        genre_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Genre,
        entity_in=genre_in,
        session=session,
    )


@router.patch("/genres/{genre_id}", response_model=NamedEntityResponse)
async def update_genre(
        genre_id: int,
        genre_in: NamedEntity,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_named_entity(
        Model=Genre,
        entity_id=genre_id,
        entity_in=genre_in,
        session=session,
    )


@router.delete("/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
        genre_id: int,
        session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Genre,
        entity_id=genre_id,
        session=session,
    )


@router.post("/stars", response_model=NamedEntityResponse)
async def create_star(
        star_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Star,
        entity_in=star_in,
        session=session,
    )


@router.patch("/stars/{star_id}", response_model=NamedEntityResponse)
async def update_star(
        star_id: int,
        star_in: NamedEntity,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_named_entity(
        Model=Star,
        entity_id=star_id,
        entity_in=star_in,
        session=session,
    )


@router.delete("/stars/{star_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_star(
        star_id: int,
        session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Star,
        entity_id=star_id,
        session=session,
    )


@router.post("/directors", response_model=NamedEntityResponse)
async def create_director(
        director_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Director,
        entity_in=director_in,
        session=session,
    )


@router.patch("/directors/{director_id}", response_model=NamedEntityResponse)
async def update_director(
        director_id: int,
        director_in: NamedEntity,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_named_entity(
        Model=Director,
        entity_id=director_id,
        entity_in=director_in,
        session=session,
    )


@router.delete(
    "/directors/{director_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_director(
        director_id: int,
        session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Director,
        entity_id=director_id,
        session=session,
    )


@router.post("/certifications", response_model=NamedEntityResponse)
async def create_certification(
        certification_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Certification,
        entity_in=certification_in,
        session=session,
    )


@router.patch(
    "/certifications/{certification_id}", response_model=NamedEntityResponse
)
async def update_certification(
        certification_id: int,
        certification_in: NamedEntity,
        session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_named_entity(
        Model=Certification,
        entity_id=certification_id,
        entity_in=certification_in,
        session=session,
    )


@router.delete(
    "/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_certification(
        certification_id: int,
        session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Certification,
        entity_id=certification_id,
        session=session,
    )
