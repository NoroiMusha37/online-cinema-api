from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",
        extra="ignore",
    )

    BASE_DIR: Path = Path(__file__).parent.parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "cinema.db")
    DATABASE_URL: str = f"sqlite+aiosqlite:///{PATH_TO_DB}"

    SECRET_KEY: str
    JWT_ENCODING_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
