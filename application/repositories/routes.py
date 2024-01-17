from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemNotInListError, ItemUpdateError, ItemCreateError
from models.routes import Route
from models.users import User


class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, route: Route):
        try:
            self.db.add(route)
            self.db.commit()
        except SQLAlchemyError as e:
            raise ItemCreateError

    def update(self, route: Route):
        try:
            self.db.query(Route).filter(Route.id == route.id).update(
                {
                    "name": route.name,
                }
            )
            self.db.commit()
        except SQLAlchemyError as e:
            raise ItemUpdateError()

    def remove_member(self, route: Route, user_to_delete: User):
        user = RouteRepository.get_member(route, user_to_delete.id)
        if not user:
            raise ItemNotInListError("Non trouvé")
        route.members.pop(route.members.index(user))
        try:
            self.update(route)
        except ItemUpdateError as e:
            raise e
        return route

    def get_route_by_id(self, route_id: str):
        return self.db.query(Route).filter(Route.id == route_id).first()

    def get_all(self):
        return self.db.query(Route).all()

    @staticmethod
    def get_member(route: Route, user_id: str):
        for member in route.members:
            if str(member.id) == str(user_id):
                return member
        return None