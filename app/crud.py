from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
import models, schemas
from typing import Annotated
from jose import JWTError, jwt
from database import get_db



def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # ambil username lalu verify pakai verify_password()
    hashed_password = schemas.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email, 
        hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

async def get_current_user(
        token: Annotated[str, Depends(schemas.oauth_2_scheme)],
        db: Session = Depends(get_db)
    ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("CHECKING USER")
    try:
        payload = jwt.decode(token, schemas.SECRET_KEY, algorithms=[schemas.ALGORITHM])
        username: str = payload.get("sub")
        print("Username :", username)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    print(f"Current Token :{token_data}")
    user = get_user(username=token_data.username, db=db)
    print("USER :",user)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("CURRENT USER =", current_user.is_active)
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user