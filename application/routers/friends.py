from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from dto.friends import FriendRequest, FriendUpdateRequest
from models.friends import Friends, FriendsStatus
from models.users import User
from repositories.friends import FriendRepository
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
    """
    Envoi une demande d'ami à un utilisateur.\n
    L'id de l'émetteur est l'id de l'utilisateur connecté.\n
    Code 404:\n
    - Si l'utilisateur cible n'existe pas\n
    - Si l'utilisateur emetteur essaye de s'ajouter lui-même en ami\n
    Code 204: Succès\n
    """
    user_repository = UserRepository(db)
    target_user = user_repository.get_user_by_id(friend_request.target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    requesting_user = user_repository.get_user_by_id(user.get('id'))
    # si l'utilisateur essaye de s'ajouter lui-même
    if requesting_user.id == target_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    friend_request_model = Friends(
        status=FriendsStatus.PENDING,
        requesting_user=requesting_user,
        target_user=target_user
    )
    friend_repository = FriendRepository(db)
    friend_repository.create(friend_request_model)
    return "created"


friends_status_possibilities = {
    FriendsStatus.PENDING: [
        FriendsStatus.ACCEPTED,
        FriendsStatus.DENIED,
    ],
    FriendsStatus.ACCEPTED: [
        FriendsStatus.REMOVED,
    ]
}


@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
def update(user: user_dependency, db: db_dependency, friend_update_request: FriendUpdateRequest):
    """
    Met à jour le status d'une demande d'ami.\n
    Seul la personne qui reçoit la demande à la permission de l'accepter ou la refuser.\n
    Les deux personnes ont la permission de supprimer une demande acceptée\n
    Code 404 :\n
    - Si la demande d'ami n'existe pas\n
    - Si la demande d'ami ne concerne pas l'utilisateur connecté.\n
    - Si l'utilisateur est concerné par la demande d'ami mais qu'il n'a pas le droit de la modifier
    (s'il est émetteur et qu'elle n'a pas encore été acceptée)\n
    Code 304:\n
    - Le nouveau status est identique à l'ancien\n
    Code 400:\n
    - Le nouveau status est impossible à appliquer (exemple : passage d'un DENIED à PENDING)
    Code 204: Succès\n
    """
    friend_repository = FriendRepository(db)
    friend_request = friend_repository.get_friend_by_id(friend_update_request.id)
    # the friend request doesn't exist
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if friend_request.status == FriendsStatus.PENDING:
        # if the user is not the target user
        if user.get('id') != str(friend_request.target_user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    elif friend_request.status == FriendsStatus.ACCEPTED:
        # if the user is not the target nor the requesting user
        if (user.get('id') != str(friend_request.target_user_id)
                and user.get('id') != str(friend_request.requesting_user_id)):

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # the status doesn't change
    if friend_request.status == friend_update_request.status:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)

    # the status change is not in the array of possibilities
    if friend_update_request.status not in friends_status_possibilities[friend_request.status]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # everything is ok, update allowed
    friend_request.status = friend_update_request.status
    friend_repository.update(friend_request)
