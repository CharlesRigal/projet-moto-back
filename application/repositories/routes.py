from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from application.exceptions.general import (
    ItemNotInListError,
    ItemCreateError,
    SelectNotFoundError,
)
from application.models.routes import Route
from application.models.users import User


class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, route: Route):
        try:
            self.db.add(route)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise ItemCreateError()

    def remove_member(self, route: Route, user_to_delete: User):
        user = RouteRepository.get_member(route, user_to_delete.id)
        route.members.pop(route.members.index(user))
        return route

    def get_route_by_id(self, route_id: UUID) -> Route:
        route = self.db.query(Route).get(route_id)
        if not route:
            raise SelectNotFoundError("Route not found")
        return route

    def get_all(self):
        return self.db.query(Route).all()

    @staticmethod
    def get_member(route: Route, user_id: str):
        for member in route.members:
            if str(member.id) == str(user_id):
                return member
        raise ItemNotInListError()
