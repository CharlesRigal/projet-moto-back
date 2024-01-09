from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import User
from repositories import users
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/{username}', status_code=status.HTTP_204_NO_CONTENT)
def username_exists(db: db_dependency, username: str):
    """get user by username"""
    user = db.query(User).filter(User.username.like(username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        id: str(user.id),
        username: user.username
    }