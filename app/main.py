from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, posts, users, vote

from .sql_app.database import engine
from .sql_app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(vote.router)
