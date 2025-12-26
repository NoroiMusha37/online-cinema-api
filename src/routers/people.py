from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_moderator
from src.models import Star, Director
from src.schemas.moderator import NamedEntityResponse, NamedEntity

from src.crud import moderator as moder_crud

people_moderator_router = APIRouter(
    prefix="/people",
    dependencies=[Depends(get_current_moderator)],
    tags=["Stars & Directors"],
)
stars_router = APIRouter(prefix="/stars")
directors_router = APIRouter(prefix="/directors")

people_moderator_router.include_router(stars_router)
people_moderator_router.include_router(directors_router)


@stars_router.post("/", response_model=NamedEntityResponse)
async def create_star(
    star_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Star,
        entity_in=star_in,
        session=session,
    )


@stars_router.patch("/{star_id}", response_model=NamedEntityResponse)
async def update_star(
    star_id: int, star_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.update_named_entity(
        Model=Star,
        entity_id=star_id,
        entity_in=star_in,
        session=session,
    )


@stars_router.delete("/{star_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_star(star_id: int, session: AsyncSession = Depends(get_db)):
    await moder_crud.delete_named_entity(
        Model=Star,
        entity_id=star_id,
        session=session,
    )


@directors_router.post("/", response_model=NamedEntityResponse)
async def create_director(
    director_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Director,
        entity_in=director_in,
        session=session,
    )


@directors_router.patch("/{director_id}", response_model=NamedEntityResponse)
async def update_director(
    director_id: int,
    director_in: NamedEntity,
    session: AsyncSession = Depends(get_db),
):
    return await moder_crud.update_named_entity(
        Model=Director,
        entity_id=director_id,
        entity_in=director_in,
        session=session,
    )


@directors_router.delete(
    "/{director_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_director(
    director_id: int, session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Director,
        entity_id=director_id,
        session=session,
    )
