from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from dto.auth import CreateUserRequest, Token
from models import User
from services.security import authenticate_user, create_jwt, get_current_user_admin
from services.utils import get_db
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from config.env import get_settings
from services.security import get_current_user
from repositories.users import get_all_users

router = APIRouter(
    prefix='/api/v1/admin',
    tags=['admin']
)
db_dependency = Annotated[Session, Depends(get_db)]
admin_dependency = Annotated[dict, Depends(get_current_user_admin)]

@router.get("/me")
def get_users(db: db_dependency, user: admin_dependency):
    user = db.query(User).filter(User.id == user.get('id')).first()
    del user.hashed_password
    return user


@router.get("/users")
def get_users(db: db_dependency, user: admin_dependency):
    """get all the users | for development only"""
    return get_all_users(db)
