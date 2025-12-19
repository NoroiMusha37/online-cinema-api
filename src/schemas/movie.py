import uuid
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


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


class SortOptions(str, Enum):
    YEAR_ASC = "year_asc"
    YEAR_DESC = "year_desc"
    TIME_ASC = "time_asc"
    TIME_DESC = "time_desc"
    IMDB_ASC = "imdb_asc"
    IMDB_DESC = "imdb_desc"
    VOTES_ASC = "votes_asc"
    VOTES_DESC = "votes_desc"
    META_SCORE_ASC = "meta_score_asc"
    META_SCORE_DESC = "meta_score_desc"
    GROSS_ASC = "gross_asc"
    GROSS_DESC = "gross_desc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class MovieQueryParameters(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    genre_ids: Optional[List[int]] = Field(None, alias="genre")
    year_from: Optional[int] = Field(None, ge=1888)
    year_to: Optional[int] = Field(None, ge=1888)
    min_time: Optional[int] = Field(None, ge=1)
    max_time: Optional[int] = Field(None, ge=1)
    min_imdb: Optional[float] = Field(None, ge=0, le=10)
    min_votes: Optional[int] = Field(None, ge=0)
    min_meta_score: Optional[int] = Field(None, ge=0, le=100)
    price_from: Optional[Decimal] = Field(None, ge=0)
    price_to: Optional[Decimal] = Field(None, ge=0)
    sort_by: SortOptions = Field(SortOptions.YEAR_DESC)

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * self.size
