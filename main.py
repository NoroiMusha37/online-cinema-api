from fastapi import FastAPI

from src.routers import auth, users, admin

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
