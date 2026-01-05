from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, DateTime, func, Numeric
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class PaymentStatusEnum(str, Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[PaymentStatusEnum] = mapped_column(
        default=PaymentStatusEnum.SUCCESSFUL
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    external_payment_id: Mapped[str | None]

    user: Mapped["User"] = relationship("User", back_populates="payments")
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    payment_items: Mapped[list["PaymentItem"]] = relationship(
        "PaymentItem", back_populates="payment", cascade="all, delete-orphan"
    )


class PaymentItem(Base):
    __tablename__ = "payment_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"), nullable=False
    )
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id"), nullable=False
    )
    price_at_payment: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    payment: Mapped["Payment"] = relationship(
        "Payment", back_populates="payment_items"
    )
    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem", back_populates="payment_items"
    )

    @hybrid_property
    def movie_name(self) -> str:
        return self.order_item.movie.name
