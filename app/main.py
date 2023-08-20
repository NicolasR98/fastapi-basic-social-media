from fastapi import FastAPI
from app.routers import posts, users, auth

from .sql_app.database import engine
from .sql_app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
