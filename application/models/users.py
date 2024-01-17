import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from models.friend import Friend
from models.routes import Route, route_member_association_table


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default="user")

    routes_owned = relationship(
        "Route",
        back_populates="owner",
        foreign_keys=[Route.owner_id],
    )
    routes_joined = relationship(
        "Route",
        secondary=route_member_association_table,
        back_populates="members",
    )

    friends_sent = relationship(
        "Friend",
        back_populates="requesting_user",
        foreign_keys=[Friend.requesting_user_id],
    )
    friends_received = relationship(
        "Friend",
        back_populates="target_user",
        foreign_keys=[Friend.target_user_id],
    )





