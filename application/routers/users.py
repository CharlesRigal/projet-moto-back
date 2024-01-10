from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.users import User
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
    """ Rechercher les utilisateurs ayant un pseudo similaire à la recherche.
     A utiliser avant d'envoyer une requete de demande d'ami
     """
    user_repository = UserRepository(db)
    users = user_repository.get_users_by_similar_username(username)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = []
    for user in users:
        data.append({'id': user.id, 'username': user.username})
    return data


# @router.get('/{id}/friends/pending', status_code=status.HTTP_200_OK)
# def search_user_by_id(db: db_dependency, user: user_dependency, id: str):
#     return id
