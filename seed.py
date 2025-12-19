import asyncio
import random
from decimal import Decimal
from sqlalchemy import select, insert
from passlib.context import CryptContext
from src.core.database import SessionLocal
from src.models.user import User, UserGroup, UserGroupEnum
from src.models.movie import Movie, Genre, Star, Director, Certification, user_favorites
from src.models.interactions import Like, Comment, Rating

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- DATA POOLS ---
GENRES = ["Action", "Sci-Fi", "Drama", "Comedy", "Horror", "Romance", "Thriller", "Fantasy"]
ACTORS = ["Leonardo DiCaprio", "Scarlett Johansson", "Robert Downey Jr.", "Margot Robbie", "Denzel Washington"]
DIRECTORS = ["Christopher Nolan", "Martin Scorsese", "Quentin Tarantino", "Greta Gerwig"]
CERTIFICATIONS = ["G", "PG", "PG-13", "R", "NC-17"]

# WRAP PRICES IN DECIMAL
MOVIES_DATA = [
    {"name": "Inception", "year": 2010, "price": Decimal("12.99"), "imdb": 8.8, "time": 148},
    {"name": "The Dark Knight", "year": 2008, "price": Decimal("14.99"), "imdb": 9.0, "time": 152},
    {"name": "Barbie", "year": 2023, "price": Decimal("19.99"), "imdb": 7.0, "time": 114},
    {"name": "Oppenheimer", "year": 2023, "price": Decimal("19.99"), "imdb": 8.5, "time": 180},
    {"name": "Pulp Fiction", "year": 1994, "price": Decimal("9.99"), "imdb": 8.9, "time": 154},
    {"name": "The Matrix", "year": 1999, "price": Decimal("11.50"), "imdb": 8.7, "time": 136},
    {"name": "Interstellar", "year": 2014, "price": Decimal("13.00"), "imdb": 8.6, "time": 169},
    {"name": "Parasite", "year": 2019, "price": Decimal("15.00"), "imdb": 8.5, "time": 132},
    {"name": "Avengers: Endgame", "year": 2019, "price": Decimal("18.00"), "imdb": 8.4, "time": 181},
    {"name": "Joker", "year": 2019, "price": Decimal("14.50"), "imdb": 8.4, "time": 122},
]


async def seed():
    async with SessionLocal() as session:
        print("🌱 Starting Database Seeding...")

        # 1. ENSURE USER GROUPS EXIST
        admin_group = await get_or_create(session, UserGroup, name=UserGroupEnum.ADMIN)
        user_group = await get_or_create(session, UserGroup, name=UserGroupEnum.USER)

        # 2. CREATE USERS LINKED TO GROUPS
        result = await session.execute(select(User).limit(1))
        if not result.scalar_one_or_none():
            user1 = User(
                email="user@example.com",
                hashed_password=pwd_context.hash("password123"),
                is_active=True,
                group_id=user_group.id
            )
            admin = User(
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True,
                group_id=admin_group.id
            )
            session.add_all([user1, admin])
            await session.commit()
            print("✅ Users created")
        else:
            print("ℹ️ Users already exist.")
            user1 = (await session.execute(select(User).where(User.email == "user@example.com"))).scalar_one()

        # 3. CREATE GENRES
        db_genres = []
        for name in GENRES:
            g = await get_or_create(session, Genre, name=name)
            db_genres.append(g)

        # 4. CREATE STARS & DIRECTORS
        db_actors = []
        for name in ACTORS:
            a = await get_or_create(session, Star, name=name)
            db_actors.append(a)

        db_directors = []
        for name in DIRECTORS:
            d = await get_or_create(session, Director, name=name)
            db_directors.append(d)

        # 5. CREATE CERTIFICATIONS
        db_certs = []
        for name in CERTIFICATIONS:
            c = await get_or_create(session, Certification, name=name)
            db_certs.append(c)

        # 6. CREATE MOVIES
        print("🎬 Creating Movies...")
        movies_list = []
        for i in range(25):
            template = MOVIES_DATA[i % len(MOVIES_DATA)]
            final_name = template["name"] if i < len(MOVIES_DATA) else f"{template['name']} {i}"

            # Pick a random certification
            cert = random.choice(db_certs)

            movie = Movie(
                name=final_name,
                description=f"Description for {final_name}.",
                year=template["year"] + random.randint(-2, 2),
                price=template["price"],
                time=template["time"],
                imdb=template["imdb"],
                votes=random.randint(100, 10000),
                meta_score=random.randint(50, 100),
                gross=random.randint(1000000, 500000000),
                certification_id=cert.id
            )

            movie.genres = random.sample(db_genres, k=random.randint(1, 3))
            movie.stars = random.sample(db_actors, k=random.randint(1, 2))
            movie.directors = [random.choice(db_directors)]

            session.add(movie)
            movies_list.append(movie)

        await session.commit()

        # 7. CREATE INTERACTIONS
        print("❤️  Adding Interactions...")

        for m in movies_list:
            await session.refresh(m)

        for movie in movies_list[:10]:
            # Like
            if random.choice([True, False]):
                session.add(Like(user_id=user1.id, movie_id=movie.id, like=True))

            # Comment
            if random.choice([True, False]):
                session.add(Comment(
                    user_id=user1.id,
                    movie_id=movie.id,
                    text=f"I really thought {movie.name} was {random.choice(['great', 'okay', 'bad'])}!"
                ))

            # Rating
            session.add(Rating(user_id=user1.id, movie_id=movie.id, score=random.randint(5, 10)))

            # Favorites (Core Table)
            if random.choice([True, False]):
                stmt = insert(user_favorites).values(
                    user_id=user1.id,
                    movie_id=movie.id
                )
                await session.execute(stmt)

        await session.commit()
        print("✨ Seeding Complete!")


async def get_or_create(session, model, **kwargs):
    stmt = select(model).filter_by(**kwargs)
    instance = (await session.execute(stmt)).scalar_one_or_none()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance


if __name__ == "__main__":
    asyncio.run(seed())