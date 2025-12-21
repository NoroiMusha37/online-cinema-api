from decimal import Decimal
from typing import Optional, List
import uuid as uuid_lib

from sqlalchemy import ForeignKey, Table, Column, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    ),
)

movie_directors = Table(
    "movie_directors",
    Base.metadata,
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "director_id",
        ForeignKey("directors.id", ondelete="CASCADE"),
        primary_key=True
    ),
)

movie_stars = Table(
    "movie_stars",
    Base.metadata,
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "star_id",
        ForeignKey("stars.id", ondelete="CASCADE"),
        primary_key=True
    ),
)

user_favorites = Table(
    "user_favorites",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    ),
)

user_movies = Table(
    "user_movies",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    movies: Mapped[List["Movie"]] = relationship(
        secondary=movie_genres, back_populates="genres"
    )


class Star(Base):
    __tablename__ = "stars"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    movies: Mapped[List["Movie"]] = relationship(
        secondary=movie_stars, back_populates="stars"
    )


class Director(Base):
    __tablename__ = "directors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    movies: Mapped[List["Movie"]] = relationship(
        secondary=movie_directors, back_populates="directors"
    )


class Certification(Base):
    __tablename__ = "certifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    movies: Mapped[List["Movie"]] = relationship(
        "Movie", back_populates="certification"
    )


class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[uuid_lib.UUID] = mapped_column(
        default=uuid_lib.uuid4, unique=True
    )
    name: Mapped[str]
    year: Mapped[int]
    time: Mapped[int]
    imdb: Mapped[float]
    votes: Mapped[int]
    meta_score: Mapped[Optional[float]]
    gross: Mapped[Optional[float]]
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    certification_id: Mapped[int] = mapped_column(ForeignKey(
        "certifications.id"
    ))
    certification: Mapped[Certification] = relationship(
        "Certification", back_populates="movies"
    )
    genres: Mapped[List[Genre]] = relationship(
        secondary=movie_genres, back_populates="movies"
    )
    directors: Mapped[List[Director]] = relationship(
        secondary=movie_directors, back_populates="movies"
    )
    stars: Mapped[List[Star]] = relationship(
        secondary=movie_stars, back_populates="movies"
    )
    likes: Mapped[List["MovieLike"]] = relationship(
        "MovieLike", back_populates="movie"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="movie"
    )
    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", back_populates="movie"
    )
    favorited: Mapped[List["User"]] = relationship(
        secondary="user_favorites", back_populates="favorites"
    )
    owners: Mapped[List["User"]] = relationship(
        secondary="user_movies", back_populates="purchased_movies"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="movie"
    )


    @property
    def certification_name(self) -> str:
        return self.certification.name

    __table_args__ = (
        UniqueConstraint(
            "name",
            "year",
            "time",
            name="uq_together_name_year_time"
        ),
    )
