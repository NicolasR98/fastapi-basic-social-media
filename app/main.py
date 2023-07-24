import time
from fastapi import FastAPI, Body, HTTPException, status
from pydantic import BaseModel
from random import randrange
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

fake_posts_db = [
    {
        "title": "post1",
        "content": "content1",
        "id": 1,
        "published": True
    },
    {
        "title": "post2",
        "content": "content3",
        "id": 2,
        "published": True
    },
    {
        "title": "post3",
        "content": "content3",
        "id": 3,
        "published": False
    },
]


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


while True:
    try:
        conn = psycopg2.connect(host='localhost', database="fastapi-social-media", user="postgres",
                                password="nrios", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("connection was successfull!")
        break
    except Exception as error:
        print("Connection failed", error)
        time.sleep(2)


def get_post_index(db, post_id: int):
    if not len(db):
        return None
    for i, post in enumerate(db):
        if post_id == post.get('id'):
            return i


def get_post(db, post_id: int):
    for post in db:
        if post_id == post['id']:
            return Post(**post)


def get_latest_post(db):
    if len(db):
        return db[-1]


@app.get("/")
def root():
    return {"message": "Hello world"}


@app.get("/posts")
def read_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.get("/posts/latest")
def read_latest_post():
    post = get_latest_post(fake_posts_db)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are not posts"
        )
    return {"payload": post}


@app.get("/posts/{id}")
def read_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    # Use triple quotation for prevent sql injection
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    # After modifiyng the db, we need to make a commit
    conn.commit()
    return {"data": new_post}


@app.put("/posts")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", str(id))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return deleted_post
