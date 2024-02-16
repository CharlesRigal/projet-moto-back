from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from exceptions.general import SelectNotFoundError
from models.users import User
from repositories.friends import FriendRepository
from repositories.users import UserRepository
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/api/v0.1/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
def search_user_by_similar_username(db: db_dependency, user: user_dependency, username: str):
    """
    Rechercher les utilisateurs ayant un pseudo similaire à la recherche.\n
    À utiliser avant d'envoyer une requête de demande d'ami\n
    Requête SQL : LIKE %username%
    """
    user_repository = UserRepository(db)
    friend_repository = FriendRepository(db)
    users = user_repository.get_users_by_similar_username(username)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    friends = []
    friends = friends + UserRepository.get_friends(user)
    friends = friends + UserRepository.get_pendings_sent(user)
    friends = friends + UserRepository.get_pendings_received(user)
    users_to_return_dict = []
    for user_ in users:
        part_of_friendship = False
        for friend in friends:
            if friend_repository.is_part_of_friendship(user_.id, friend):
                part_of_friendship = True
        if not part_of_friendship:
            users_to_return_dict.append(user_.to_dict(only=('id', 'username')))
    return users_to_return_dict


