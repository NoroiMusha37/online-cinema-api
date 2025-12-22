import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import convert_movie_uuid_to_id
from src.schemas.interactions import CommentPage
from src.schemas.movie import (
    MovieQueryParameters,
    MoviePage,
    MovieDetail,
    GenreList
)
from src.crud import movie as movie_crud
from src.crud import interactions as inter_crud
from src.utils.pagination import paginate

router = APIRouter(prefix="/movies")


@router.get("/", response_model=MoviePage)
async def get_movies(
        params: MovieQueryParameters = Depends(),
        session: AsyncSession = Depends(get_db)
):
    movies, count = await movie_crud.get_movies(params=params, session=session)
    return paginate(
        items=movies,
        count=count,
        page=params.page,
        size=params.size,
        path="/movies/"
    )


@router.get("/genres", response_model=GenreList)
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
        path="/movies/genres/"
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


@router.get("/genres/{uuid}/comments", response_model=CommentPage)
async def get_comments(
        movie_id: int = Depends(convert_movie_uuid_to_id),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        session: AsyncSession = Depends(get_db),
):
    movie = await movie_crud.get_movie_by_id(movie_id, session=session)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )

    comments, count = await inter_crud.get_comments_by_movie(
        movie_id=movie_id, page=page, size=size, session=session
    )

    return paginate(
        items=comments,
        count=count,
        page=page,
        size=size,
        path="/movies/genres/{uuid}/comments/"
    )
