from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class MovieBase(BaseModel):
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    certification_id: int


class MovieCreate(MovieBase):
    genre_ids: List[int]
    star_ids: List[int]
    director_ids: List[int]


class MovieUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    time: Optional[int] = None
    imdb: Optional[float] = None
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    certification_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None
    star_ids: Optional[List[int]] = None
    director_ids: Optional[List[int]] = None


class NamedEntity(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class GenreCreate(NamedEntity):
    pass


class GenreUpdate(NamedEntity):
    pass


class StarCreate(NamedEntity):
    pass


class StarUpdate(NamedEntity):
    pass


class DirectorCreate(NamedEntity):
    pass


class DirectorUpdate(NamedEntity):
    pass


class CertificationCreate(NamedEntity):
    pass


class CertificationUpdate(NamedEntity):
    pass
