from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from dto.friends import FriendCreateRequest, FriendUpdateRequest
from exceptions.general import SelectNotFoundError, InvalidJWTError, ItemCreateError, ItemUpdateError
from models.friend import Friend, FriendsStatus
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
def send_friend_request(requesting_user: user_dependency, db: db_dependency, friend_request: FriendCreateRequest):
    """
    Envoi une demande d'ami à un utilisateur.\n
    L'id de l'émetteur est l'id de l'utilisateur connecté.\n
    Code 404:\n
    - "target-user-not-found": Si l'utilisateur cible n'existe pas\n
    - "cant-request-oneself": Si l'utilisateur emetteur essaye de s'ajouter lui-même en ami\n
    Code 204: Succès\n
    Code 500 "creation-failure": erreur dans la création au niveau de la bdd\n
    """
    # TODO : remove routes member of friend is revoked
    user_repository = UserRepository(db)
    try:
        target_user = user_repository.get_user_by_id(friend_request.target_user_id)
    except SelectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="target-user-not-found")

    # si l'utilisateur essaye de s'ajouter lui-même
    if str(requesting_user.id) == str(target_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cant-request-oneself")
    friend_request_model = Friend(
        status=FriendsStatus.PENDING,
        requesting_user=requesting_user,
        target_user=target_user
    )
    friend_repository = FriendRepository(db)
    try:
        friend_repository.create(friend_request_model)
    except ItemCreateError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="creation-failure")
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
    - "friend-request-not-found": Si la demande d'ami n'existe pas
    ou la demande d'ami ne concerne pas l'utilisateur connecté.\n
    Code 403 "not-allowed" : Si l'utilisateur est concerné par la demande d'ami mais qu'il n'a pas le droit de la modifier
    (s'il est émetteur et qu'elle n'a pas encore été acceptée)\n
    Code 304 "unchanged" : Le nouveau status est identique à l'ancien\n
    Code 400 "status-not-possible" : Le nouveau status est impossible à appliquer (exemple : passage d'un DENIED à PENDING)
    Code 204: Succès\n
    Code 500 "update-failure": erreur dans la mise à jour au niveau de la bdd\n

    """
    friend_repository = FriendRepository(db)

    # the friend request doesn't exist
    try:
        friend_request = friend_repository.get_friend_by_id(friend_update_request.id)
    except SelectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="friend-request-not-found")

        # the connected user is not part of this friendship
    if not FriendRepository.is_part_of_friendship(user.id, friend_request):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="friend-request-not-found")

    if friend_request.status == FriendsStatus.PENDING:
        # if the user is not the target user
        if str(user.id) != str(friend_request.target_user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not-allowed")

    # the status doesn't change
    if friend_request.status == friend_update_request.status:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="unchanged")

    # the status change is not in the array of possibilities
    if friend_update_request.status not in friends_status_possibilities[friend_request.status]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status-not-possible")

    # everything is ok, update allowed
    friend_request.status = friend_update_request.status
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure")

@router.get('/', status_code=status.HTTP_200_OK)
def get_friends(db: db_dependency, user: user_dependency,pending_sent: bool = None,
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
    friends = []
    if not pending_sent and not pending_received:
        friends = friends + UserRepository.get_friends(user)
    if pending_sent:
        friends = friends + UserRepository.get_pendings_sent(user)
    if pending_received:
        friends = friends + UserRepository.get_pendings_received(user)
    to_return_friends = []
    for friend in friends:
        to_return_friends.append(friend.to_dict())
    return to_return_friends
