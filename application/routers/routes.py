from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from dto.friends import FriendCreateRequest, FriendUpdateRequest
from dto.routes import RouteCreateRequest, MemberAddRequest
from dto.waypoints import WayPointCreateRequest, WayPointEditRequest
from exceptions.general import ItemNotInListError, ItemUpdateError, ItemCreateError, SelectNotFoundError, \
    InvalidJWTError
from models.friend import Friend, FriendsStatus
from models.routes import Route
from models.waypoint import Waypoint
from models.users import User
from repositories.friends import FriendRepository
from repositories.routes import RouteRepository
from repositories.users import UserRepository
from repositories.waypoints import WaypointRepository
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/routes',
    tags=['routes']
)

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_route(db: db_dependency, user: user_dependency, route: RouteCreateRequest):
    """Crée un voyage de type privé dont le propriétaire est l'utilisateur connecté.\n
    Code 422: Erreur de validation\n
    Code 201: succès\n
    Code 500 "creation-failure": erreur dans la création au niveau de la bdd\n
    """
    route_model = Route(
        name=route.name,
        description=route.description,
        owner=user,
        is_public=False
    )
    route_repository = RouteRepository(db)
    try:
        route_repository.create(route_model)
    except ItemCreateError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="creation-failure")


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_own_route(db: db_dependency, user: user_dependency, owned: bool = False, joined: bool = False):
    """Récupère tous les voyages en lien à l'utilisateur connecté, en laissant le choix de choisir les
    voyages rejoint, possédés, ou les deux."""
    to_return = []
    if joined:
        to_return = to_return + user.routes_joined
    if owned:
        to_return = to_return + user.routes_owned
    return to_return


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
    except SelectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")
    if str(user.id) != str(route.owner_id):
        found = False
        for _user in route.members:
            if str(_user.id) == str(user.id):
                found = True
                break
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")
    return route


@router.post('/{route_id}/members', status_code=status.HTTP_201_CREATED)
def add_member(db: db_dependency, user: user_dependency, route_id: str, member: MemberAddRequest):
    """
    Ajoute un ami au trajet\n
    Code 404:\n
    - "route-not-found": le trajet n'existe pas ou l'utilisateur n'en est pas le propriétaire\n
    - "friend-not-found": l'utilisateur n'a pas d'ami ayant cet id
    """
    route_repository = RouteRepository(db)
    user_repository = UserRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")

    if str(route.owner_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")

    friend_user = UserRepository.get_friend(user, member.id)
    if not friend_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user-not-part-of-route")
    route.members.append(friend_user)
    route_repository.update(route)
    return route


@router.delete('/{route_id}/members', status_code=status.HTTP_200_OK)
def remove_member(db: db_dependency, user: user_dependency, route_id: str, member_to_delete_request: MemberAddRequest):
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")

    try:
        user_to_delete = user_repository.get_user_by_id(member_to_delete_request.id)
    except SelectNotFoundError:
        # l'utilisateur cible n'existe pas
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user-not-part-of-the-route")

    # si l'utilisateur connecté n'est ni propriétaire du trajet ni l'utilisateur à supprimer
    if str(user.id) != str(route.owner.id) and str(user.id) != str(user_to_delete.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='route-not-found')

    try:
        route_repository.remove_member(route, user_to_delete)
    except ItemNotInListError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user-not-part-of-the-route")
    except ItemUpdateError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="update-failure")

    return route.members


@router.post('/{route_id}/waypoints', status_code=status.HTTP_200_OK)
def add_waypoint(db: db_dependency, user: user_dependency, route_id: UUID, waypoint_request: WayPointCreateRequest):
    """
    Ajoute un point a un itinéraire
    Code 200: point crée
    Code 404:
    "route-not-found": la route n'existe pas ou l'utilisateur n'a pas les droits dessus
    """
    route_repository = RouteRepository(db)
    waypoint_repository = WaypointRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")

    try:
        RouteRepository.get_member(route, user.id)
    except ItemNotInListError:
        if route.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")
    waypoint_model = Waypoint(
        name=waypoint_request.name,
        latitude=waypoint_request.latitude,
        longitude=waypoint_request.longitude,
        order=len(route.waypoints),
        route=route
    )
    waypoint_repository.create(waypoint_model)
    return waypoint_model


@router.patch('/{route_id}')
def edit_waypoint(db: db_dependency, user: user_dependency, route_id: UUID, waypoint: WayPointEditRequest):
    """Permet d'éditer un point de trajet. Cela inclut l'echanger de l'ordre avec un autre point de trajet.\n
    Code 400: "order-out-of-range" : le nouvel ordre ne correspond pas a un autre point de trajet """
    route_repository = RouteRepository(db)
    waypoint_repository = WaypointRepository(db)
    try:
        route = route_repository.get_route_by_id(route_id)
    except SelectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")
    try:
        RouteRepository.get_member(route, user.id)
    except ItemNotInListError:
        if route.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="route-not-found")

    try:
        original_waypoint = waypoint_repository.get_waypoint_by_id(waypoint.id)

        if original_waypoint.route.id != route_id:
            raise SelectNotFoundError()

    except SelectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="waypoint-not-found")
    route.waypoints
    return route

    if original_waypoint.order != waypoint.order:
        try:
            other_waypoint = WaypointRepository.get_waypoint_by_order(route, waypoint.order)
        except ItemNotInListError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="order-out-of-range")
        route = WaypointRepository.swap_waypoints(original_waypoint, other_waypoint)

    return waypoint
