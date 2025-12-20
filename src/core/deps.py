import uuid

from jose import jwt, JWTError
from sqlalchemy import select
from starlette import status

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.models.movie import Movie
from src.models.user import User, UserGroupEnum
from src.schemas.user import TokenPayload
import src.crud.user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ENCODING_ALGORITHM],
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise credentials_exception

        if token_data.sub is None:
            raise credentials_exception

    except (JWTError, ValidationError):
        raise credentials_exception

    user = await user_crud.get_user_by_id(
        user_id=int(token_data.sub), session=session
    )

    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin(
        current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.group.name != UserGroupEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_current_moderator(
        current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.group.name == UserGroupEnum.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


async def convert_movie_uuid_to_id(
        movie_uuid: uuid.UUID,
        session: AsyncSession = Depends(get_db)
) -> int:
    result = await session.execute(select(Movie.id)
                                  .where(Movie.uuid == movie_uuid))
    movie_id = result.scalar_one_or_none()
    if not movie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return movie_id
