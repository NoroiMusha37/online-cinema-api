from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from .commons import BasePagination


class CartCreate(BaseModel):
    user_id: int


class CartItemCreate(BaseModel):
    movie_id: int


class CartMovie(BaseModel):
    name: str
    price: Decimal
    genres: list[str]
    year: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("genres", mode="before")
    @classmethod
    def flatten_genres(cls, genres: list["Genre"]) -> list[str]:
        return [genre.name for genre in genres]


class CartItemResponse(BaseModel):
    id: int
    movie: CartMovie

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BasePagination):
    items: list[CartItemResponse]

    @computed_field
    def total_price(self) -> Decimal:
        return sum((item.movie.price for item in self.items), Decimal("0.0"))


class ModeratorCartItemResponse(CartItemResponse):
    added_at: datetime


class ModeratorCartResponse(BasePagination):
    user_id: int
    items: list[ModeratorCartItemResponse]

    @computed_field
    def total_price(self) -> Decimal:
        return sum((item.movie.price for item in self.items), Decimal("0.0"))
