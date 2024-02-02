from typing import Union, Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from schemas import (
    fake_users_db, 
    authenticate_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    create_access_token, 
    Token,
    Login, 
    UserCreate, 
    ItemCreate,
    Item,
    Users,
    UserBase
) 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models
from database import get_db, engine

models.Base.metadata.create_all(bind=engine)

# models.Base.metadata.create_all(bind=engine)

# # docker-compose run api alembic revision --autogenerate -m "init"
# # docker-compose exec postgres psql -U alifvianmarco -d irisdb
# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://0.0.0.0:8502"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incoret username of password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me", response_model=Users)
async def read_users_me(
    current_user: Annotated[UserBase ,Depends(crud.get_current_active_user)], 
    db: Session = Depends(get_db)
):
    current_user = crud.get_user(db=db, username=current_user)
    print("CURRENT USER IN MAIN =", current_user)
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[Users, Depends(crud.get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    return {
        "status":"200",
        "msg":"User Created",
        "user":user.username
    }


@app.get("/users/", response_model=List[Users])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=Users)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=dict) #response_model=Item before
def create_item_for_user(
    user_id: int, 
    item: ItemCreate, 
    current_user: UserBase = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db)
):
    print("current_user_id =",current_user.id, "user_id =",user_id)
    if current_user.id == user_id:
        item_create = crud.create_user_item(db=db, item=item, user_id=user_id)
        return {
            "status":"200",
            "msg":"User Created",
            "item":item_create.title
        }
    else:
        raise HTTPException(status_code=401, detail="Authenticated user not as the same as input user id parameter")


@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items