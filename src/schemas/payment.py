from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.models.payment import PaymentStatusEnum
from src.schemas.commons import BasePagination


class PaymentItemBase(BaseModel):
    order_item_id: int
    price_at_payment: Decimal


class PaymentItemResponse(PaymentItemBase):
    id: int
    payment_id: int
    movie_name: str
    model_config = ConfigDict(from_attributes=True)


class PaymentItemCreate(PaymentItemBase):
    pass


class PaymentList(BaseModel):
    id: int
    order_id: int
    created_at: datetime
    status: PaymentStatusEnum
    amount: Decimal
    external_payment_id: str
    model_config = ConfigDict(from_attributes=True)


class PaymentDetail(PaymentList):
    payment_items: list[PaymentItemResponse]


class PaymentResponse(BasePagination):
    items: list[PaymentList]


class PaymentCreate(BaseModel):
    user_id: int
    order_id: int
    amount: Decimal
    external_payment_id: str
    status: PaymentStatusEnum = PaymentStatusEnum.SUCCESSFUL


class StripeSessionRequest(BaseModel):
    order_id: int


class StripeSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
