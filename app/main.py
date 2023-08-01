from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import schemas
from .sql_app import models
from .sql_app.database import engine, get_db
from .sql_app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/posts", response_model=list[schemas.Post])
def read_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/latest", response_model=schemas.Post)
def read_latest_post(db: Session = Depends(get_db)):
    post_query = db.query(models.Post).order_by(models.Post.id.desc())
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are not posts"
        )
    return post


@app.get("/posts/{id}", response_model=schemas.Post)
def read_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.put("/posts", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    post.delete(synchronize_session=False)
    db.commit()
