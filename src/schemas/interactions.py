from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from src.schemas.movie import MovieList
from .commons import BasePagination


class LikeAction(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class LikeCreate(BaseModel):
    liked: bool


class LikeResponse(BaseModel):
    action: LikeAction
    state: Optional[bool]

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    text: str = Field(max_length=512)
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    text: str
    created_at: datetime
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CommentPage(BasePagination):
    items: List[CommentResponse]


class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=10)


class RatingResponse(BaseModel):
    user_id: int
    movie_id: int
    score: int

    model_config = ConfigDict(from_attributes=True)


class RatingList(RatingResponse):
    movie: MovieList


class RatingPage(BasePagination):
    items: List[RatingList]
