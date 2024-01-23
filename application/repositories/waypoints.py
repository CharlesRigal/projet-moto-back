from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemNotInListError, ItemUpdateError, ItemCreateError, SelectNotFoundError
from models.routes import Route
from models.waypoint import Waypoint
from models.users import User


class WaypointRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, waypoint: Waypoint):
        try:
            self.db.add(waypoint)
            self.db.commit()
        except SQLAlchemyError:
            raise ItemCreateError()

    def get_waypoint_by_id(self, route_id: str):
        route = self.db.query(Waypoint).filter(Waypoint.id == route_id).first()
        if not route:
            raise SelectNotFoundError()
        return route

    @staticmethod
    def swap_waypoints(self, route: Route, waypoint1: Waypoint, waypoint2: Waypoint):
        index_waypoint1 = route.waypoints.index(waypoint1)
        index_waypoint2 = route.waypoints.index(waypoint2)
        route.waypoints[index_waypoint1].order, route.waypoints[index_waypoint2].order = route.waypoints[
            index_waypoint2].order, \
            route.waypoints[index_waypoint1].order
        return route

    @staticmethod
    def get_waypoint_by_order(route: Route, order: int):
        for waypoint in route.waypoints:
            if waypoint.order == order:
                return waypoint
        raise ItemNotInListError()
