from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from exceptions.general import SelectNotFoundError
from models.friend import Friend, FriendsStatus
from models.routes import Route
from models.users import User
from services.security import get_current_user_admin
from services.utils import get_db
from repositories.users import UserRepository

router = APIRouter(prefix="/api/v0.1/admin", tags=["admin"])
db_dependency = Annotated[Session, Depends(get_db)]
admin_dependency = Annotated[dict, Depends(get_current_user_admin)]


@router.get("/generate-data")
def generate_data(db: db_dependency):
    hashed_pass = bcrypt.hashpw("fake")
    user = User(
        username="user1",
        email="email@example.com",
        hashed_password=hashed_pass,
        is_active=True,
        role="admin",
    )
    db.add(user)
    user2 = User(
        username="user2",
        email="email2@example.com",
        hashed_password=hashed_pass,
        is_active=True,
        role="user",
    )
    db.add(user2)
    user3 = User(
        username="user3",
        email="email3@example.com",
        hashed_password=hashed_pass,
        is_active=True,
        role="user",
    )
    db.add(user3)
    db.commit()
    friend = Friend(
        requesting_user=user, target_user=user2, status=FriendsStatus.ACCEPTED
    )
    friend2 = Friend(
        requesting_user=user, target_user=user3, status=FriendsStatus.PENDING
    )
    db.add(friend)
    db.add(friend2)
    db.commit()
    route = Route(
        name="gorges de la nesque",
        description="balade sympa",
        owner=user,
        members=[user2],
    )
    db.add(route)
    db.commit()


@router.get("/me")
def admin_guard(db: db_dependency, user: admin_dependency):
    """
    Verifies si l'utilisateur courant est admin.
    A utiliser comme guard admin
    """
    user_repository = UserRepository(db)
    try:
        user = user_repository.get_user_by_id(user.id)
    except SelectNotFoundError:
        # this is not supposed to happen because admin_dependency already fetch the user and raise an exception if not found
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error"
        )
    del user.hashed_password
    return user


@router.get("/users")
def get_users(db: db_dependency, user: admin_dependency):
    """
    Récupère la liste des utilisateurs.
    À utiliser en dev uniquement.
    """
    user_repository = UserRepository(db)
    return user_repository.get_all()
