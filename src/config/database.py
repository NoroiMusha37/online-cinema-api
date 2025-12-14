from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.config.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
