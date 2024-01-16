from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from dto.friends import FriendCreateRequest, FriendUpdateRequest
from dto.trips import TripCreateRequest
from models.friend import Friend, FriendsStatus
from models.trips import Trip
from models.users import User
from repositories.friends import FriendRepository
from repositories.trips import TripRepository
from repositories.users import UserRepository
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/api/v1/trips',
    tags=['trips']
)

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trip(db: db_dependency, user: user_dependency, trip: TripCreateRequest):
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(user.get('id'))
    trip_model = Trip(
        name=trip.name,
        description=trip.description,
        owner=user,
        is_public=False
    )
    trip_repository = TripRepository(db)
    trip_repository.create(trip_model)


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_own_trip(db: db_dependency, user: user_dependency, owned: bool = False, joined: bool = False):
    """Récupère tous les voyages en lien à l'utilisateur connecté, en laissant le choix de choisir les
    voyages rejoint, possédés, ou les deux."""
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(user.get('id'))
    to_return = []
    if joined:
        to_return = to_return + user.trips_joined
    if owned:
        to_return = to_return + user.trips_owned
    return to_return


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_one_trip(db: db_dependency, user: user_dependency, id: str):
    """Vérifie si l'utilisateur participe ou possède ce voyage puis retourne ses données"""
    trip_repository = TripRepository(db)
    trip = trip_repository.get_trip_by_id(id)
    if user.get('id') != str(trip.owner_id):
        found = False
        for _user in trip.members:
            if str(_user.id) == user.get('id'):
                found = True
                break
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return trip
