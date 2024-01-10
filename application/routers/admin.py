from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.users import User
from services.security import get_current_user_admin
from services.utils import get_db
from repositories.users import get_all_users, UserRepository

router = APIRouter(
    prefix='/api/v1/admin',
    tags=['admin']
)
db_dependency = Annotated[Session, Depends(get_db)]
admin_dependency = Annotated[dict, Depends(get_current_user_admin)]

@router.get("/me")
def admin_guard(db: db_dependency, user: admin_dependency):
    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user.get('id'))
    del user.hashed_password
    return user


@router.get("/users")
def get_users(db: db_dependency, user: admin_dependency):
    """get all the users | for development only"""
    return get_all_users(db)
