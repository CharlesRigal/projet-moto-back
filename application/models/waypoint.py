from config.database import Base

import uuid

from sqlalchemy import (
    Column,
    UUID,
    String,
    Boolean,
    Table,
    ForeignKey,
    Text,
    DECIMAL,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin


class Waypoint(Base, SerializerMixin):
    __tablename__ = "waypoints"
    serialize_rules = ("-route.waypoints",)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    latitude = Column(DECIMAL(precision=8, scale=6), index=True)
    longitude = Column(DECIMAL(precision=9, scale=6), index=True)
    name = String(100)
    order = Column(Integer)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"))

    route = relationship(
        "Route",
        foreign_keys=[route_id],
        back_populates="waypoints",
    )

    # def __eq__(self, other):
    #     return self.id == other.id
