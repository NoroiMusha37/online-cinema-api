import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_active_user
from src.core.security import hash_password, verify_password
from src.models.user import User
from src.schemas.movie import MoviePage, MovieQueryParameters
from src.schemas.user import (
    UserRead,
    UserProfileRead,
    UserProfileUpdate,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserPasswordChange,
)
from src.crud import user as user_crud
from src.crud import token as token_crud
from src.crud import movie as movie_crud
from src.tasks.email_tasks import send_reset_password_email_task
from src.utils.pagination import paginate

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserRead)
async def read_users_me(
        current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.patch("/me/profile", response_model=UserProfileRead)
async def update_my_profile(
        profile_in: UserProfileUpdate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    return await user_crud.update_profile(
        user_id=current_user.id,
        profile_in=profile_in,
        session=session
    )


@router.post("/password-reset")
async def password_reset(
        payload: UserPasswordChange,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    if not verify_password(
            payload.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    new_password = hash_password(payload.new_password)

    await user_crud.update_password(
        user_id=current_user.id,
        new_password=new_password,
        session=session
    )

    return {"message": "Password reset successful"}


@router.post("/password-reset/request")
async def password_reset_request(
        payload: PasswordResetRequest,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_user_by_email(
        email=str(payload.email), session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is inactive"
        )

    token_str = secrets.token_urlsafe(32)
    await token_crud.create_password_reset_token(
        user_id=user.id,
        token=token_str,
        session=session
    )
    send_reset_password_email_task.delay(str(user.email), token_str)

    return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm")
async def password_reset_confirm(
        payload: PasswordResetConfirm,
        session: AsyncSession = Depends(get_db)
):
    reset_token = await token_crud.get_password_reset_token(
        token=payload.token, session=session
    )

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    if reset_token.expires_at < datetime.now(timezone.utc):
        await token_crud.delete_password_reset_token(
            token=reset_token.token, session=session
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )

    hashed_password = hash_password(payload.new_password)

    await session.execute(
        update(User)
        .where(User.id == reset_token.user_id)
        .values(hashed_password=hashed_password)
    )
    await token_crud.delete_password_reset_token(
        token=reset_token.token, session=session
    )

    return {"message": "Password updated successfully"}


@router.get("/me/favorites", response_model=MoviePage)
async def get_favorites(
        current_user: User = Depends(get_current_active_user),
        params: MovieQueryParameters = Depends(),
        session: AsyncSession = Depends(get_db)
):
    favorites, count = await movie_crud.get_user_favorites(
        user_id=current_user.id,
        params=params,
        session=session
    )

    return paginate(
        items=favorites,
        count=count,
        page=params.page,
        size=params.size,
    )


@router.get("/me/likes", response_model=MoviePage)
async def get_likes(
        liked: bool,
        current_user: User = Depends(get_current_active_user),
        params: MovieQueryParameters = Depends(),
        session: AsyncSession = Depends(get_db)
):
    likes, count = await movie_crud.get_user_like_movies(
        user_id=current_user.id,
        params=params,
        session=session,
        liked=liked
    )

    return paginate(
        items=likes,
        count=count,
        page=params.page,
        size=params.size,
    )
