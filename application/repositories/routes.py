from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemNotInListError, ItemUpdateError, ItemCreateError, SelectNotFoundError
from models.routes import Route
from models.users import User
import logging

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
        try:
            user = RouteRepository.get_member(route, user_to_delete.id)
        except ItemNotInListError as e:
            raise e
        route.members.pop(route.members.index(user))
        return route

    def get_route_by_id(self, route_id: str):
        route = self.db.query(Route).filter(Route.id == route_id).first()
        if not route:
            raise SelectNotFoundError()
        return route

    def get_all(self):
        return self.db.query(Route).all()

    @staticmethod
    def get_member(route: Route, user_id: str):
        for member in route.members:
            if str(member.id) == str(user_id):
                return member
        raise ItemNotInListError()
