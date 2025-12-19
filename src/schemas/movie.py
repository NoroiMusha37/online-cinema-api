import uuid
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from fastapi import Query
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
    movie_count: int


class GenreList(BasePagination):
    items: List[GenreWithCount]


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
    items: List[MovieList]


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


class MovieQueryParameters:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
        genre_ids: Optional[List[int]] = Query(None, alias="genre"),
        year_from: Optional[int] = Query(None, ge=1888),
        year_to: Optional[int] = Query(None, ge=1888),
        min_time: Optional[int] = Query(None, ge=1),
        max_time: Optional[int] = Query(None, ge=1),
        min_imdb: Optional[float] = Query(None, ge=0, le=10),
        min_votes: Optional[int] = Query(None, ge=0),
        min_meta_score: Optional[int] = Query(None, ge=0, le=100),
        price_from: Optional[Decimal] = Query(None, ge=0),
        price_to: Optional[Decimal] = Query(None, ge=0),
        sort_by: SortOptions = Query(SortOptions.YEAR_DESC),
    ):
        self.page = page
        self.size = size
        self.search = search
        self.genre_ids = genre_ids
        self.year_from = year_from
        self.year_to = year_to
        self.min_time = min_time
        self.max_time = max_time
        self.min_imdb = min_imdb
        self.min_votes = min_votes
        self.min_meta_score = min_meta_score
        self.price_from = price_from
        self.price_to = price_to
        self.sort_by = sort_by

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
