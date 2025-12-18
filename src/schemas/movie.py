import uuid
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class BasePagination(BaseModel):
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
    model_config = ConfigDict(from_attributes=True)



class GenreResponse(BaseResponse):
    pass


class GenreWithCount(BaseResponse):
    count: int


class GenreList(BasePagination):
    genres: List[GenreWithCount]


class StarResponse(BaseResponse):
    pass


class DirectorResponse(BaseResponse):
    pass


class CertificationResponse(BaseResponse):
    pass


class MovieBase(BaseModel):
    id: int
    uuid: uuid.UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: Decimal
    genres: List[GenreResponse]

    model_config = ConfigDict(from_attributes=True)


class MovieList(MovieBase):
    certification_name: str


class MovieDetail(MovieBase):
    certification: CertificationResponse
    stars: List[StarResponse]
    directors: List[DirectorResponse]
    comment_count: int = 0


class MoviePage(BasePagination):
    movies: List[MovieList]
