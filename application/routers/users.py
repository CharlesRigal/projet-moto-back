from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user
from starlette import status

from application.repositories.friends import FriendRepository
from application.repositories.users import UserRepository
from application.services.security import get_current_user
from application.services.utils import get_db

from application.models.users import User

from application.services.security import authenticate_user, get_current_user_admin

router = APIRouter(prefix="/api/v0.1/users", tags=["users"])

db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)

@router.delete("/remove_my_self", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = db_dependency
):
    """
    Deletes the account of the currently authenticated user.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password of the user.
        db (Session, optional): The database session dependency. Defaults to db_dependency.

    Raises:
        HTTPException: Raised if the user is not authenticated or if deletion fails.

    Returns:
        Response: A response with status code 204 (No Content) if the deletion is successful.
    """
    my_self = authenticate_user(db, form_data.username, form_data.password)
    if UserRepository(db).delete_user(my_self):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        username: str,
        get_current_user_admin = Depends(),
        db: Session = db_dependency
):
    """
    Deletes a user by their username.

    Args:
        username (str): The username of the user to delete.
        user_admin (User): The current user who is an admin.
        db (Session, optional): The database session dependency. Defaults to db_dependency.

    Raises:
        HTTPException: Raised if the user is not authorized to perform the deletion.

    Returns:
        Response: A response with status code 204 (No Content) if the deletion is successful,
        or status code 404 (Not Found) if the user to delete is not found.
    """
    user_repository = UserRepository(db)

    if not user_repository.delete_user(username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
