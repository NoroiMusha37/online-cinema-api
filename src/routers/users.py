import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_active_user
from src.core.security import hash_password
from src.models.user import User
from src.schemas.user import UserRead, UserProfileRead, UserProfileUpdate, PasswordResetRequest, PasswordResetConfirm
from src.crud import user as user_crud
from src.crud import token as token_crud

router = APIRouter(prefix="/users")


def send_reset_email(email: str, token: str):
    print(f"Reset sent to {email}")


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
    background_tasks.add_task(send_reset_email, str(user.email), token_str)

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
