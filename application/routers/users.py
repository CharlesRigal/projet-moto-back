from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.users import User
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', status_code=status.HTTP_204_NO_CONTENT)
def search_user_by_similar_username(db: db_dependency, username: str):
    """get user by similar username. for use in friend search"""
    user = db.query(User).filter(User.username == f'%{username}').first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        id: str(user.id),
        username: user.username
    }