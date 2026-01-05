from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.models.order import OrderStatusEnum
from src.schemas.commons import BasePagination


class OrderMovieResponse(BaseModel):
    id: int
    name: str
    year: int
    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    movie: OrderMovieResponse
    price_at_order: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    movie_id: int
    price_at_order: Decimal


class OrderCreate(BaseModel):
    items: list[int]


class OrderBase(BaseModel):
    id: int
    created_at: datetime
    status: OrderStatusEnum
    total_amount: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderDetail(OrderBase):
    items: list[OrderItemResponse]


class OrderList(OrderBase):
    items_names: list[str]


class OrderResponse(BasePagination):
    items: list[OrderList]


class OrderUpdate(BaseModel):
    status: OrderStatusEnum | None = None
