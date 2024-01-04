from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import User
from repositories import users
from repositories.users import get_all_users
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/")
def get_users(db: db_dependency):
    """get all the users | for development only"""
    return get_all_users()

