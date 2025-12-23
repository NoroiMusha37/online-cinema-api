from datetime import date, datetime
from enum import Enum

from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from src.core.database import Base


class UserGroupEnum(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class GenderEnum(str, Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"


class UserGroup(Base):
    __tablename__ = "user_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[UserGroupEnum] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    group_id: Mapped[int] = mapped_column(ForeignKey(
        "user_groups.id", ondelete="CASCADE")
    )

    group: Mapped[UserGroup] = relationship(
        "UserGroup", back_populates="users"
    )
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    activation_token: Mapped["ActivationToken"] = relationship(
        "ActivationToken",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    password_reset_token: Mapped["PasswordResetToken"] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    movies_likes: Mapped[list["MovieLike"]] = relationship(
        "MovieLike", back_populates="user"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="user"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating", back_populates="user"
    )
    favorites: Mapped[list["Movie"]] = relationship(
        secondary="user_favorites", back_populates="favorited"
    )
    comments_likes: Mapped[list["CommentLike"]] = relationship(
        "CommentLike", back_populates="user"
    )
    purchased_movies: Mapped[list["Movie"]] = relationship(
        secondary="user_movies", back_populates="owners"
    )
    cart: Mapped["Cart"] = relationship(
        "Cart", back_populates="user", uselist=False
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    first_name: Mapped[str]
    last_name: Mapped[str]
    avatar: Mapped[str | None]
    gender: Mapped[GenderEnum | None]
    date_of_birth: Mapped[date | None]
    info: Mapped[str | None]

    user: Mapped[User] = relationship("User", back_populates="profile")


class TokenMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ActivationToken(Base, TokenMixin):
    __tablename__ = "activation_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    user: Mapped[User] = relationship(
        "User", back_populates="activation_token"
    )


class PasswordResetToken(Base, TokenMixin):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    user: Mapped[User] = relationship(
        "User", back_populates="password_reset_token"
    )


class RefreshToken(Base, TokenMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")
