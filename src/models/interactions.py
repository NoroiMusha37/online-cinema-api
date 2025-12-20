from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from src.core.database import Base


class MovieLike(Base):
    __tablename__ = "movies_likes"
    like: Mapped[bool]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship("User", back_populates="movies_likes")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="likes")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"
    ))
    movie_id: Mapped[int] = mapped_column(ForeignKey(
        "movies.id", ondelete="CASCADE"
    ))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey(
        "comments.id", ondelete="CASCADE"
    ))
    user: Mapped["User"] = relationship("User", back_populates="comments")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="parent"
    )
    likes: Mapped[List["CommentLike"]] = relationship(
        "CommentLike", back_populates="comment"
    )


class Rating(Base):
    __tablename__ = "ratings"
    score: Mapped[int]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="ratings")

    __table_args__ = (
        CheckConstraint(
            "score >= 1 AND score <= 10", name="check_score_range"
        ),
    )


class CommentLike(Base):
    __tablename__ = "comments_likes"
    like: Mapped[bool]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="comments_likes"
    )
    comment: Mapped["Comment"] = relationship(
        "Comment", back_populates="likes"
    )
