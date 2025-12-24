from fastapi import Query, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_moderator
from src.models import Genre, Certification
from src.schemas.moderator import NamedEntityResponse, NamedEntity
from src.schemas.movie import GenreList

from src.crud import movie as movie_crud
from src.crud import moderator as moder_crud
from src.utils.pagination import paginate


router = APIRouter(tags=["Genres & Certifications"])

genre_router = APIRouter(prefix="/genres")
moderator_router = APIRouter(dependencies=[Depends(get_current_moderator)])
certifications_moderator_router = APIRouter(
    prefix="/certifications", dependencies=[Depends(get_current_moderator)]
)

genre_router.include_router(moderator_router)
router.include_router(genre_router)
router.include_router(certifications_moderator_router)



@genre_router.get("/", response_model=GenreList)
async def get_genres(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        session: AsyncSession = Depends(get_db),
):
    genres, count = await movie_crud.get_genres_with_counts(
        page=page, size=size, session=session
    )

    return paginate(
        items=genres,
        count=count,
        page=page,
        size=size,
        path="/genres/"
    )


@moderator_router.post("/", response_model=NamedEntityResponse)
async def create_genre(
        genre_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Genre,
        entity_in=genre_in,
        session=session,
    )


@moderator_router.patch("/{genre_id}", response_model=NamedEntityResponse)
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


@moderator_router.delete(
    "/{genre_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_genre(
        genre_id: int,
        session: AsyncSession = Depends(get_db)
):
    await moder_crud.delete_named_entity(
        Model=Genre,
        entity_id=genre_id,
        session=session,
    )


certifications_moderator_router = APIRouter(
    prefix="/certifications", dependencies=[Depends(get_current_moderator)]
)

@certifications_moderator_router.post(
    "/",
    response_model=NamedEntityResponse
)
async def create_certification(
        certification_in: NamedEntity, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_named_entity(
        Model=Certification,
        entity_in=certification_in,
        session=session,
    )


@certifications_moderator_router.patch(
    "/{certification_id}",
    response_model=NamedEntityResponse
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


@certifications_moderator_router.delete(
    "/{certification_id}",
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
