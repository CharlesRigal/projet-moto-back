from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import User
from repositories.users import UserRepository
from services.utils import get_db

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/api/v1/users")
def get_users(db: db_dependency):
    """get all the users | for development only"""
    return db.query(User).all()

