from fastapi import FastAPI

from src.routers import (
    auth,
    user,
    movie,
    interactions,
    metadata,
    people,
    cart,
    order,
    payment,
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(interactions.router)
app.include_router(movie.router)
app.include_router(metadata.router)
app.include_router(people.people_moderator_router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(payment.router)
