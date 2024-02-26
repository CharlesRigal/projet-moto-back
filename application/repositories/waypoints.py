from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemCreateError, SelectNotFoundError
from models.routes import Route
from models.waypoint import Waypoint


class WaypointRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, waypoint: Waypoint):
        try:
            self.db.add(waypoint)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise ItemCreateError()

    def get_waypoint_by_id(self, route_id: str):
        route = self.db.query(Waypoint).filter(Waypoint.id == route_id).first()
        if not route:
            raise SelectNotFoundError()
        return route


    @staticmethod
    def swap_waypoints(route: Route, waypoint1: Waypoint, waypoint2: Waypoint):
        waypoint1.order, waypoint2.order = waypoint2.order, waypoint1.order
        return waypoint1, waypoint2

    def get_waypoint_by_order(self, route: Route, order: int):
        waypoint = self.db.query(Waypoint).filter(Waypoint.route_id == route.id and Waypoint.order == order).first()
        if not waypoint:
            raise SelectNotFoundError()
        return waypoint