from typing import Annotated

from fastapi import Security, APIRouter, Depends
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from repositories import users as users_repo
from config.database import SessionLocal
from models import User
from services.utils import get_db

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/api/v1/auth/signup", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Create a user account"""
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()
    return {'success': True}
