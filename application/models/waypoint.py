from sqlalchemy import Column, UUID, String, ForeignKey, DECIMAL, Integer
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from config.database import Base
import uuid

class Waypoint(Base, SerializerMixin):
    __tablename__ = "waypoints"
    serialize_rules = ("-route.waypoints", "-user.waypoints")
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    latitude = Column(DECIMAL(precision=8, scale=6), index=True)
    longitude = Column(DECIMAL(precision=9, scale=6), index=True)
    name = Column(String(100))
    order = Column(Integer)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user = relationship("User", back_populates="waypoints", lazy="selectin")
    route = relationship("Route", back_populates="waypoints", lazy="selectin")
