from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.core.database import get_db
from src.core.deps import (
    get_current_user,
    convert_movie_uuid_to_id,
    get_current_active_user,
)
from src.models.interactions import Comment
from src.models.user import User
from src.schemas.interactions import (
    LikeCreate,
    CommentResponse,
    CommentCreate,
    RatingResponse,
    RatingCreate,
    CommentPage,
    RatingPage,
)
from src.crud import interactions as inter_crud
from src.crud import movie as movie_crud
from src.schemas.movie import MoviePage, MovieQueryParameters
from src.tasks.email_tasks import send_comment_notification_email_task
from src.utils.pagination import paginate

router = APIRouter(prefix="/movies", tags=["Interactions"])


@router.get("/me", response_model=MoviePage)
async def get_purchased_movies(
    params: MovieQueryParameters = Depends(),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    movies, count = await movie_crud.get_movies(
        params=params,
        session=session,
        user_id=current_user.id,
    )

    return paginate(
        items=movies,
        count=count,
        page=params.page,
        size=params.size,
        path="/movies/me",
    )


@router.post("/{uuid}/like")
async def like_movie(
    like_in: LikeCreate,
    movie_id: int = Depends(convert_movie_uuid_to_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await inter_crud.toggle_movie_like(
        movie_id=movie_id,
        user_id=current_user.id,
        liked=like_in,
        session=session,
    )


@router.get("/{uuid}/comments", response_model=CommentPage)
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
        path="/movies/{uuid}/comments/",
    )


@router.post("/{uuid}/comments", response_model=CommentResponse)
async def create_comment(
    comment_in: CommentCreate,
    movie_id: int = Depends(convert_movie_uuid_to_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    new_comment = await inter_crud.create_comment(
        movie_id=movie_id,
        user_id=current_user.id,
        comment=comment_in,
        session=session,
    )

    if comment_in.parent_id:
        stmt = (
            select(Comment)
            .options(selectinload(Comment.user), selectinload(Comment.movie))
            .where(Comment.id == comment_in.parent_id)
        )
        result = await session.execute(stmt)
        parent_comment = result.scalar_one_or_none()

        if parent_comment and parent_comment.user_id != current_user.id:
            send_comment_notification_email_task.delay(
                parent_comment.user.email,
                comment_in.parent_id,
                parent_comment.movie.name,
            )

    return new_comment


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    success = await inter_crud.delete_comment(
        comment_id=comment_id, user_id=current_user.id, session=session
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return {"message": "Comment deleted"}


@router.post("/{movie_uuid}/rate", response_model=RatingResponse)
async def rate_movie(
    rating_in: RatingCreate,
    movie_id: int = Depends(convert_movie_uuid_to_id),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await inter_crud.upsert_rating(
        movie_id=movie_id,
        user_id=user.id,
        rating_in=rating_in,
        session=session,
    )


@router.post("/{movie_uuid}/favorite")
async def favorite_movie(
    movie_id: int = Depends(convert_movie_uuid_to_id),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    result = await inter_crud.toggle_favorite(
        movie_id=movie_id, user_id=user.id, session=session
    )
    if not result:
        return {"message": "Movie removed from favorites"}

    return {"message": "Movie added to favorites"}


@router.post("/comments/{comment_id}/like")
async def like_comment(
    like_in: LikeCreate,
    comment_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await inter_crud.toggle_comment_like(
        comment_id=comment_id, user_id=user.id, liked=like_in, session=session
    )


@router.get("/favorites/me", response_model=MoviePage)
async def get_favorites(
    current_user: User = Depends(get_current_active_user),
    params: MovieQueryParameters = Depends(),
    session: AsyncSession = Depends(get_db),
):
    favorites, count = await movie_crud.get_user_favorites(
        user_id=current_user.id, params=params, session=session
    )

    return paginate(
        items=favorites,
        count=count,
        page=params.page,
        size=params.size,
        path="/movies/favorites/me/",
    )


@router.get("/likes/me", response_model=MoviePage)
async def get_movie_likes(
    liked: bool,
    current_user: User = Depends(get_current_active_user),
    params: MovieQueryParameters = Depends(),
    session: AsyncSession = Depends(get_db),
):
    likes, count = await movie_crud.get_user_liked_movies(
        user_id=current_user.id, params=params, session=session, liked=liked
    )

    return paginate(
        items=likes,
        count=count,
        page=params.page,
        size=params.size,
        path="/movies/likes/me/",
    )


@router.get("/comments/likes/me", response_model=CommentPage)
async def get_comment_likes(
    liked: bool,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    comments, count = await movie_crud.get_user_liked_comments(
        user_id=current_user.id,
        liked=liked,
        page=page,
        size=size,
        session=session,
    )

    return paginate(
        items=comments,
        count=count,
        page=page,
        size=size,
        path="/movies/comments/likes/me/",
    )


@router.get("/ratings/me", response_model=RatingPage)
async def get_ratings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    ratings, count = await movie_crud.get_user_rated_movies(
        user_id=current_user.id, page=page, size=size, session=session
    )
    return paginate(
        items=ratings,
        count=count,
        page=page,
        size=size,
        path="/movies/ratings/me/",
    )
