import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_moderator
from src.schemas.moderator import MovieCreate, MovieUpdate
from src.schemas.movie import MovieQueryParameters, MoviePage, MovieDetail
from src.crud import movie as movie_crud
from src.crud import moderator as moder_crud
from src.utils.pagination import paginate

router = APIRouter(prefix="/movies", tags=["Movies"])
moderator_router = APIRouter(dependencies=[Depends(get_current_moderator)])

router.include_router(moderator_router)


@router.get("/", response_model=MoviePage)
async def get_movies(
    params: MovieQueryParameters = Depends(),
    session: AsyncSession = Depends(get_db),
):
    movies, count = await movie_crud.get_movies(params=params, session=session)
    return paginate(
        items=movies,
        count=count,
        page=params.page,
        size=params.size,
        path="/movies/",
    )


@router.get("/{uuid}", response_model=MovieDetail)
async def get_movie(
    movie_uuid: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    movie = await movie_crud.get_movie_by_uuid(
        movie_uuid=movie_uuid, session=session
    )

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )

    return movie


@moderator_router.post("/", response_model=MovieDetail)
async def create_movie(
    movie_in: MovieCreate, session: AsyncSession = Depends(get_db)
):
    return await moder_crud.create_movie(
        movie_in=movie_in,
        session=session,
    )


@moderator_router.patch("/{movie_id}", response_model=MovieDetail)
async def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    session: AsyncSession = Depends(get_db),
):
    return await moder_crud.update_movie(
        movie_id=movie_id,
        movie_in=movie_in,
        session=session,
    )


@moderator_router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, session: AsyncSession = Depends(get_db)):
    return await moder_crud.delete_movie(
        movie_id=movie_id,
        session=session,
    )
