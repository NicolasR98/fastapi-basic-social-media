from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import oauth2, schemas
from app.sql_app import models
from app.sql_app.database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[schemas.Post])
def read_posts(db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).all()
    return posts


@router.get("/latest", response_model=schemas.Post)
def read_latest_post(db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).order_by(models.Post.id.desc())
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are not posts"
        )
    return post


@router.get("/{id}", response_model=schemas.Post)
def read_post(id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    print(current_user)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.put("/", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    post.delete(synchronize_session=False)
    db.commit()
