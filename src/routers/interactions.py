from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_user, convert_movie_uuid_to_id
from src.models.user import User
from src.schemas.interactions import LikeCreate, CommentResponse, CommentCreate, RatingResponse, RatingCreate
from src.crud import interactions as inter_crud

router = APIRouter(prefix="/movies")


@router.post("/{uuid}/like")
async def like_movie(
        like_in: LikeCreate,
        movie_id: int = Depends(convert_movie_uuid_to_id),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await inter_crud.upsert_like(
        movie_id=movie_id,
        user_id=current_user.id,
        liked=like_in,
        session=session
    )


@router.delete("/{uuid}/like")
async def delete_like(
        movie_id: int = Depends(convert_movie_uuid_to_id),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    await inter_crud.delete_like(
        movie_id=movie_id,
        user_id=current_user.id,
        session=session
    )
    return {"message": "Like/dislike removed"}


@router.post("/{uuid}/comments", response_model=CommentResponse)
async def create_comment(
        comment_in: CommentCreate,
        movie_id: int = Depends(convert_movie_uuid_to_id),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
):
    return await inter_crud.create_comment(
        movie_id=movie_id,
        user_id=current_user.id,
        comment=comment_in,
        session=session
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
        comment_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
):
    success = await inter_crud.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        session=session
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
        session=session
    )


@router.post("/{movie_uuid}/favorite")
async def favorite_movie(
        movie_id: int = Depends(convert_movie_uuid_to_id),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
):
    result = await inter_crud.toggle_favorite(
        movie_id=movie_id,
        user_id=user.id,
        session=session
    )
    if not result:
        return {"message": "Movie removed from favorites"}

    return {"message": "Movie added to favorites"}
