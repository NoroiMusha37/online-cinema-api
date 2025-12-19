from fastapi import FastAPI

from src.routers import auth, user, admin, movie, interactions

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(movie.router)
app.include_router(interactions.router)