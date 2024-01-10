from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from dto.friends import FriendRequest
from models.friends import Friends, FriendsStatus
from models.users import User
from repositories.users import UserRepository
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/friends',
    tags=['friends']
)

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def send_friend_request(user: user_dependency, db: db_dependency, friend_request: FriendRequest):
    """Send a friend request to a user"""
    user_repository = UserRepository(db)
    target_user = user_repository.get_by_id(friend_request.target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    requesting_user = user_repository.get_by_id(user.get('id'))
    if requesting_user.id == target_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    friend_request_model = Friends(
        status=FriendsStatus.PENDING,
        requesting_user=requesting_user,
        target_user=target_user
    )
    # db.add(friend_request_model)
    return friend_request_model
