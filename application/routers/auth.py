from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status

from dto.auth import CreateUserRequest, Token, PasswordResetRequest
from models import User
from services.security import authenticate_user, create_jwt
from services.utils import get_db
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from config.env import get_settings
from services.security import get_current_user

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['auth']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

SECRET_KEY = get_settings().jwt_secret_key
ALGORITHM = get_settings().jwt_algorithm
DELTA_HOURS = get_settings().jwt_expire_hours
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Create a user account"""
    user = db.query(User).filter(User.email == create_user_request.email).first()
    if user:
        return {'details': [{
            "type": 'already_used',
            "loc": [
                "body",
                "email"
            ],
            "msg": "Already used",
            'input': create_user_request
        }]}
    user = db.query(User).filter(User.username == create_user_request.username).first()
    if user:
        return {'details': [{
            "type": 'already_used',
            "loc": [
                "body",
                "username"
            ],
            "msg": "Already used",
            'input': create_user_request
        }]}
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()
    return {'success': True}


@router.post("/signin", status_code=status.HTTP_200_OK, response_model=Token)
def login_for_jwt(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                  db: db_dependency):
    """Log in a user and retrieve a JWT token.
        The username is the email !!!
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect")
    user = db.query(User).filter(User.email == form_data.username).first()
    token = create_jwt(user, timedelta(hours=DELTA_HOURS))
    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user(current_user: user_dependency, db: db_dependency):
    user = db.query(User).filter(User.id == current_user.get('id')).first()
    del user.hashed_password
    return user


@router.get('/username/{username}', status_code=status.HTTP_204_NO_CONTENT)
def username_exists(db: db_dependency, username: str):
    """Check if username exists in database. To use in the register form"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password_request: PasswordResetRequest):
    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(password_request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password")
    user_model.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.add(user_model)
    db.commit()
