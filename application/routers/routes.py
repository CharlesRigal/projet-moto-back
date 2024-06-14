from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from dto.routes import RouteCreateRequest, MemberAddRequest
from dto.waypoints import WayPointCreateRequest
from exceptions.general import (
    ItemNotInListError,
    ItemCreateError,
    SelectNotFoundError,
)
from models.routes import Route
from models.users import User
from models.waypoint import Waypoint
from repositories.routes import RouteRepository
from repositories.users import UserRepository
from services.security import get_current_user
from services.utils import get_db
from routers.websocket import (
    send_message_to_other_user_of_route_except_sender,
)

router = APIRouter(prefix="/api/v0.1/routes", tags=["routes"])

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[User, Depends(get_current_user)]


@router.put("/{route_id}", status_code=status.HTTP_200_OK)
async def update_route(
    route_id: UUID,
    db: db_dependency,
    user: user_dependency,
    route_update: RouteCreateRequest,
):
    route_repository = RouteRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
        print(route.waypoints)
    except SelectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )

    if route.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    if route_update.date:
        try:
            route.date = route_update.date
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="invalid-date-format",
            )
    else:
        route.date = datetime.now()

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure"
        )

    return route.to_dict()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_route(db: db_dependency, user: user_dependency, route: RouteCreateRequest):
    """Crée un voyage de type privé dont le propriétaire est l'utilisateur connecté.\n
    Code 422: Erreur de validation\n
    Code 201: succès\n
    Code 500 "creation-failure": erreur dans la création au niveau de la bdd\n
    """
    waypoints = []
    for waypoint in route.waypoints:
        waypoints.append(
            Waypoint(
                name=waypoint.name,
                latitude=waypoint.latitude,
                longitude=waypoint.longitude,
                order=waypoint.order,
            )
        )
    route_model = Route(
        name=route.name,
        description=route.description,
        owner=user,
        is_public=False,
        waypoints=waypoints,
    )
    route_repository = RouteRepository(db)
    try:
        route_repository.create(route_model)
    except ItemCreateError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="creation-failure"
        )
    return route_model.to_dict()


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_own_route(
    db: db_dependency, user: user_dependency, owned: bool = False, joined: bool = False
):
    """Récupère tous les voyages en lien à l'utilisateur connecté, en laissant le choix de choisir les
    voyages rejoint, possédés, ou les deux."""
    to_return = []
    if joined:
        to_return = to_return + user.routes_joined
    if owned:
        to_return = to_return + user.routes_owned
    to_return_dict = []
    for to_return_ in to_return:
        to_return_dict.append(to_return_.to_dict())
    return to_return_dict


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_one_route(db: db_dependency, user: user_dependency, id: str):
    """
    Vérifie si l'utilisateur participe ou possède ce voyage puis retourne ses données.\n
    Code 404:\n
    - "route-not-found": le trajet n'exsite pas ou l'utilisateur n'en est ni propriétaire, ni membre\n
    """
    route_repository = RouteRepository(db)
    try:
        route = route_repository.get_route_by_id(id)
    except SelectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )
    if str(user.id) != str(route.owner_id):
        found = False
        for _user in route.members:
            if str(_user.id) == str(user.id):
                found = True
                break
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
            )
    return route.to_dict()


@router.post("/{route_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    db: db_dependency, user: user_dependency, route_id: str, member: MemberAddRequest
):
    """
    Ajoute un ami au trajet\n
    Code 404:\n
    - "route-not-found": le trajet n'existe pas ou l'utilisateur n'en est pas le propriétaire\n
    - "friend-user-id-not-found": l'utilisateur n'a pas d'ami ayant cet id
    Code 409 "friend-already-member": l'utilisateur fait deja partie de la route
    """
    route_repository = RouteRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )

    if str(route.owner_id) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )

    try:
        friend_user = UserRepository.get_friend_user(user, member.id)
    except ItemNotInListError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="friend-user-id-not-found"
        )

    if friend_user in route.members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="friend-already-member"
        )

    route.members.append(friend_user)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure"
        )
    return route


@router.delete("/{route_id}/members", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    db: db_dependency,
    user: user_dependency,
    route_id: str,
    member_to_delete_request: MemberAddRequest,
):
    """Si utilisateur propriétaire du voyage: supprime un des membres\n
    Si utilisateur membre du voyage: Retire ce voyage de ses voyages rejoint\n
    Code 404:\n
    - "user-not-part-of-the-route" : L'utilisateur cible n'existe pas ou n'est pas membre du trajet\n
    - "route-not-found" : Le trajet n'existe pas ou l'utilisateur n'en est pas membre\n
    Code 500 "update-failure": erreur dans la mise à jour au niveau de la bdd\n
    """
    route_repository = RouteRepository(db)
    user_repository = UserRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )

    try:
        user_to_delete = user_repository.get_user_by_id(member_to_delete_request.id)
    except SelectNotFoundError:
        # l'utilisateur cible n'existe pas
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user-not-part-of-the-route"
        )

    # si l'utilisateur connecté n'est ni propriétaire du trajet ni l'utilisateur à supprimer
    if str(user.id) != str(route.owner.id) and str(user.id) != str(user_to_delete.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )
    try:
        route_repository.remove_member(route, user_to_delete)

    except ItemNotInListError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user-not-part-of-the-route"
        )
    try:
        db.commit()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure"
        )


@router.put("/{route_id}/waypoints", status_code=status.HTTP_200_OK)
async def update_waypoints(
    db: db_dependency,
    user: user_dependency,
    route_id: UUID,
    waypoint_request: list[WayPointCreateRequest],
):
    """
    Remplace la liste de waypoints de la route par la nouvelle liste.
    Supprime tous les waypoints et les recrée dans la foulée\n
    Code 200: points crées\n
    Code 404:
    "route-not-found": la route n'existe pas ou l'utilisateur n'a pas les droits dessus\n
    Code 500 "update-failure": erreur au niveau de la base de données
    """
    route_repository = RouteRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
        )
    try:
        RouteRepository.get_member(route, user.id)
    except ItemNotInListError:
        if route.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found"
            )
    waypoints = []
    for waypoint in waypoint_request:
        waypoints.append(
            Waypoint(
                name=waypoint.name,
                latitude=waypoint.latitude,
                longitude=waypoint.longitude,
                order=waypoint.order,
            )
        )
    try:
        db.query(Waypoint).filter(Waypoint.route_id == route.id).delete()
        route.waypoints = waypoints
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure"
        )
    await send_message_to_other_user_of_route_except_sender(
        user, route, {"route-uuid": str(route.id)}
    )
    return waypoints
