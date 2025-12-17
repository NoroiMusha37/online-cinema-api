from datetime import datetime, timezone, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.config import settings
from src.models.user import RefreshToken, ActivationToken, PasswordResetToken


async def create_refresh_token(
        user_id: int, token: str, session: AsyncSession
) -> RefreshToken:
    expires_at = (datetime.now(timezone.utc)
                  + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )

    session.add(refresh_token)
    await session.commit()
    return refresh_token


async def get_refresh_token(
        token: str, session: AsyncSession
) -> RefreshToken | None:
    result = await session.execute(select(RefreshToken)
                                   .where(RefreshToken.token == token))
    return result.scalar_one_or_none()


async def delete_refresh_token(token: str, session: AsyncSession) -> None:
    await session.execute(delete(RefreshToken)
                          .where(RefreshToken.token == token))
    await session.commit()


async def create_activation_token(
        user_id: int, token: str, session: AsyncSession
) -> ActivationToken:
    await session.execute(delete(ActivationToken)
                          .where(ActivationToken.user_id == user_id)
                          )
    expires_at = (datetime.now(timezone.utc)
                  + timedelta(hours=settings.ACCOUNT_ACTIVATION_HOURS))
    activation_token = ActivationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )

    session.add(activation_token)
    await session.commit()
    return activation_token


async def get_activation_token(
        token: str, session: AsyncSession
) -> ActivationToken | None:
    result = await session.execute(select(ActivationToken)
                                   .where(ActivationToken.token == token)
                                   )
    return result.scalar_one_or_none()


async def delete_activation_token(token: str, session: AsyncSession) -> None:
    await session.execute(delete(ActivationToken)
                          .where(ActivationToken.token == token))
    await session.commit()


async def create_password_reset_token(
        user_id: int, token: str, session: AsyncSession
) -> PasswordResetToken:
    await session.execute(delete(PasswordResetToken)
                          .where(PasswordResetToken.user_id == user_id))
    expires_at = (datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    ))
    password_reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )

    session.add(password_reset_token)
    await session.commit()
    return password_reset_token


async def get_password_reset_token(
        token: str, session: AsyncSession
) -> PasswordResetToken | None:
    result = await session.execute(select(PasswordResetToken)
                                   .where(PasswordResetToken.token == token)
                                   )
    return result.scalar_one_or_none()


async def delete_password_reset_token(
        token: str, session: AsyncSession
) -> None:
    await session.execute(delete(PasswordResetToken)
                          .where(PasswordResetToken.token == token)
                          )
    await session.commit()
