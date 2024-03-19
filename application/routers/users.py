from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette import status

from repositories.users import UserRepository
from services.security import get_current_user
from services.utils import get_db

from models.users import User

router = APIRouter(prefix="/api/v0.1/users", tags=["users"])

db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    username: str, db: Session = db_dependency, user: User = user_dependency
):
    """
    Deletes a user by their username.

    Args:
        username (str): The username of the user to delete.
        db (Session, optional): The database session dependency. Defaults to db_dependency.
        user (User, optional): The current user dependency. Defaults to user_dependency.

    Raises:
        HTTPException: Raised if the user is not authorized to perform the deletion.

    Returns:
        Response: A response with status code 204 (No Content) if the deletion is successful,
        or status code 404 (Not Found) if the user to delete is not found.
    """
    user_repository = UserRepository(db)
    user_to_remove = user_repository.get_user_by_username(username)
    if user.role == "admin" or user.username == username:
        if not user_repository.delete_user(user_to_remove):
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.get("/", status_code=status.HTTP_200_OK)
def search_user_by_similar_username(
    username: str, db: Session = db_dependency, user: User = user_dependency
):
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
            users_to_return_dict.append(user_.to_dict(only=("id", "username")))
    return users_to_return_dict
