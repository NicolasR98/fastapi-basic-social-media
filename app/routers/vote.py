from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import oauth2, schemas
from app.sql_app import database, models

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", response_model=schemas.Vote)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {vote.post_id} does not exist",
        )

    query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id,
    )
    found_vote = query.first()

    if vote.dir == schemas.VoteEnum.vote:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} alredy vote on post",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return vote

    if not found_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {current_user.id} can't remove vote if it does not exist",
        )
    query.delete()
    db.commit()
    return vote
