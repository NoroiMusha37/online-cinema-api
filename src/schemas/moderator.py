from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class MovieBase(BaseModel):
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    certification_id: int


class MovieCreate(MovieBase):
    genre_ids: int | None
    star_ids: int | None
    director_ids: int | None


class MovieUpdate(BaseModel):
    name: str | None = None
    year: int | None = None
    time: int | None = None
    imdb: float | None = None
    votes: int | None = None
    meta_score: float | None = None
    gross: float | None = None
    description: str | None = None
    price: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    certification_id: int | None = None
    genre_ids: list[int] | None = None
    star_ids: list[int] | None = None
    director_ids: list[int] | None = None


class NamedEntity(BaseModel):
    name: str


class NamedEntityResponse(NamedEntity):
    id: int
    model_config = ConfigDict(from_attributes=True)
