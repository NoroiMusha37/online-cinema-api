from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ENCODING_ALGORITHM,
    )
    return encoded_jwt


def create_access_token(user_id: int):
    return create_token(
        data={"sub": str(user_id), "type": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int):
    return create_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
