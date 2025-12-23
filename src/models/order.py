from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, func, Numeric, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class StatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[StatusEnum] = mapped_column(
        default=StatusEnum.PENDING, nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    @hybrid_property
    def items_names(self) -> list[str]:
        return [item.movie.name for item in self.items]


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id"), nullable=False
    )
    price_at_order: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    order: Mapped[Order] = relationship("Order", back_populates="items")
    movie: Mapped["Movie"] = relationship(
        "Movie", back_populates="order_items"
    )
