from fastapi import FastAPI

from app.routers import auth, posts, users, vote

from .sql_app.database import engine
from .sql_app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(vote.router)
