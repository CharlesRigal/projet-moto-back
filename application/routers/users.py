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
    prefix='/api/v1/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
def search_user_by_similar_username(db: db_dependency, username: str):
    """
    Rechercher les utilisateurs ayant un pseudo similaire à la recherche.\n
    À utiliser avant d'envoyer une requête de demande d'ami\n
    Requête SQL : LIKE %username%
    """
    user_repository = UserRepository(db)
    users = user_repository.get_users_by_similar_username(username)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = []
    for user in users:
        data.append({'id': user.id, 'username': user.username})
    return data


@router.get('/{id}/friends', status_code=status.HTTP_200_OK)
def get_friends(db: db_dependency, user: user_dependency, id: str, pending_sent: bool = None,
                pending_received: bool = None):
    """
    Récupère la liste d'ami de l'utilisateur.\n
    Il n'est possible d'utiliser cette requête que sur l'utilisateur connecté.\n
    Si pending_sent = False et pending_received = False: renvoie la liste d'amis.\n
    Si pending_sent = True : renvoie la liste des demandes d'amis envoyés en attente.\n
    Si pending_received = True : renvoie la liste des demandes d'amis recues en attente.\n
    Il est possible de combiner pending_sent = True et pending_received = True\n
    Code 404: Si l'utilisateur connecté essaye de récupérer les amis de quelqu'un d'autre / quelqu'un qui n'existe pas\n
    Code 200: Succès\n
    """
    if str(user.id) != id:  # if the user try to get information from someone else
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    user_repository = UserRepository(db)

    friends = []
    if not pending_sent and not pending_received:
        friends = friends + UserRepository.get_friends(user)
    if pending_sent:
        friends = friends + UserRepository.get_pendings_sent(user)
    if pending_received:
        friends = friends + UserRepository.get_pendings_received(user)
    return friends
