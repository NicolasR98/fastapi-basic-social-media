from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import schemas
from app.sql_app import database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="LOGIN")

SECRET_KEY = "411ab86f3280a8914105a204e1c6bfdb0381fcea6f6a150d5d20128dcb16315c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exeption):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get('user_id')

        if id is None:
            raise credentials_exeption
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exeption
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token = verify_access_token(token, credentials_exeption)

    return db.query(models.User).filter(models.User.id == token.id).first()
