import uuid

from sqlalchemy import Column, UUID, String, Boolean, Table, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
from models.waypoint import Waypoint
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

route_member_association_table = Table(
    "route_member_association_table",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("route_id", ForeignKey("routes.id"), primary_key=True),
)


class Route(Base, SerializerMixin):
    __tablename__ = "routes"
    serialize_rules = [
        "-owner.routes_joined",
        "-owner.routes_owned",
        "-owner.friends_sent",
        "-owner.friends_received",
        "-owner.role",
        "-owner.email",
        "-members.routes_joined",
        "-members.routes_owned",
        "-members.friends_sent",
        "-members.friends_received",
        "-members.role",
        "-members.email",
        "-waypoints.route",
    ]
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100))
    description = Column(Text())
    is_public = Column(Boolean())
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="routes_owned",
        lazy="selectin",
    )

    members = relationship(
        "User",
        secondary=route_member_association_table,
        back_populates="routes_joined",
        lazy="selectin",
    )

    waypoints = relationship(
        "Waypoint",
        back_populates="route",
        foreign_keys=[Waypoint.route_id],
        lazy="selectin",
        cascade="all, delete",
    )
