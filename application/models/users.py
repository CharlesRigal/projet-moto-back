from enum import Enum
from typing import Optional
from fastapi import WebSocket
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from config.database import Base
from models.friend import Friend
from models.routes import Route, route_member_association_table
from services.WebsocketRegistry import WebSocketRegistry

websockets_registry = WebSocketRegistry()


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base, SerializerMixin):
    __tablename__ = "users"
    serialize_rules = (
        "-hashed_password",
        "-routes_owned.owner",
        "-routes_joined.members",
        "-friends_sent.requesting_user",
        "-friends_received.target_user",
        "-waypoints",
    )
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default=Role.USER)

    def have_role(self, role: str) -> bool:
        return self.role == role

    @property
    def websocket(self) -> Optional[WebSocket]:
        return websockets_registry.get_websocket_by_user_uuid(self.id)

    @websocket.setter
    def websocket(self, websocket: WebSocket):
        websockets_registry.add_websocket(self.id, websocket)

    @websocket.deleter
    def websocket(self):
        websockets_registry.remove_websocket(self.id)

    routes_owned = relationship(
        "Route",
        back_populates="owner",
        foreign_keys=[Route.owner_id],
        lazy="selectin",
        join_depth=1,
        cascade="all, delete",
    )

    routes_joined = relationship(
        "Route",
        secondary=route_member_association_table,
        back_populates="members",
        lazy="selectin",
        join_depth=1,
        cascade="all, delete",
    )

    friends_sent = relationship(
        "Friend",
        back_populates="requesting_user",
        foreign_keys=[Friend.requesting_user_id],
        lazy="selectin",
        join_depth=1,
        cascade="all,delete",
    )

    friends_received = relationship(
        "Friend",
        back_populates="target_user",
        foreign_keys=[Friend.target_user_id],
        lazy="selectin",
        join_depth=1,
        cascade="all,delete",
    )

    waypoints = relationship("Waypoint", back_populates="user", lazy="selectin")

    def __str__(self):
        return f"User: {self.username}"
