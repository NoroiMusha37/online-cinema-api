import secrets
from datetime import timezone, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.security import verify_password, create_access_token
from src.models.user import User
from src.schemas.user import UserRead, UserCreate, Token
from src.crud import user as user_crud
from src.crud import token as token_crud
from src.tasks.email_tasks import send_activation_email_task

router = APIRouter(prefix="/auth")


@router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register(
        user_in: UserCreate,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_db)
):
    user = await user_crud.create_user(user_in=user_in, session=session)
    token_str = secrets.token_urlsafe(32)

    await token_crud.create_activation_token(
        user_id=user.id,
        token=token_str,
        session=session,
    )

    send_activation_email_task.delay(str(user.email), token_str)
    return user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_user_by_email(
        email=form_data.username, session=session
    )

    if not user or not verify_password(
            form_data.password, str(user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user."
                   "Please check your email for activation link.",
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token_str = secrets.token_urlsafe(32)
    await token_crud.create_refresh_token(
        user_id=user.id,
        token=refresh_token_str,
        session=session,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_tokens(
        refresh_token: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_db),
):
    db_token = await token_crud.get_refresh_token(
        token=refresh_token, session=session
    )
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if db_token.expires_at < datetime.now(timezone.utc):
        await token_crud.delete_refresh_token(
            token=refresh_token, session=session
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    access_token = create_access_token(user_id=db_token.user_id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/logout")
async def logout(
        refresh_token: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_db),
):
    await token_crud.delete_refresh_token(
        token=refresh_token, session=session
    )
    return {"message": "Successfully logged out"}


@router.post("/activate")
async def activate_account(
        token: str,
        session: AsyncSession = Depends(get_db),
):
    activation_token = await token_crud.get_activation_token(
        token=token, session=session
    )
    if not activation_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )

    if activation_token.expires_at < datetime.now(timezone.utc):
        await token_crud.delete_activation_token(token=token, session=session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    await session.execute(
        update(User)
        .where(User.id == activation_token.user_id)
        .values(is_active=True)
    )

    await token_crud.delete_activation_token(token=token, session=session)
    return {"message": "Account activated successfully"}
