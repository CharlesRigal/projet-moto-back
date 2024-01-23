import uuid

from sqlalchemy import Column, UUID, String, Boolean, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from models.waypoint import Waypoint
route_member_association_table = Table(
    "route_member_association_table",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("route_id", ForeignKey("routes.id"), primary_key=True)
)


class Route(Base):
    __tablename__ = 'routes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100))
    description = Column(Text())
    is_public = Column(Boolean())
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="routes_owned",
    )

    members = relationship(
        "User",
        secondary=route_member_association_table,
        back_populates="routes_joined",
    )

    waypoints = relationship(
        "Waypoint",
        back_populates="route",
        foreign_keys=[Waypoint.route_id],
    )


