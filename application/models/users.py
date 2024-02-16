import uuid

from sqlalchemy import Column, String, Boolean, UUID
from sqlalchemy.orm import relationship

from config.database import Base
from models.friend import Friend
from models.routes import Route, route_member_association_table
from sqlalchemy_serializer import SerializerMixin
from fastapi import WebSocket


class User(Base, SerializerMixin):

    __tablename__ = 'users'
    serialize_rules = (
        '-hashed_password',
        '-routes_owned', '-routes_owned',
        '-routes_joined', '-routes_joined',
        '-friends_sent', '-friends_sent',
        '-friends_received', '-friends_received',
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default="user")

    def __init__(self, *args):
        self._active_connection = None
        self.super(self, *args)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connection = websocket

    async def get_websocket(self) -> WebSocket:
        return self._active_connection

    routes_owned = relationship(
        "Route",
        back_populates="owner",
        foreign_keys=[Route.owner_id],
        lazy="selectin",
        join_depth=1
    )

    routes_joined = relationship(
        "Route",
        secondary=route_member_association_table,
        back_populates="members",
        lazy="selectin",
        join_depth=1
    )

    friends_sent = relationship(
        "Friend",
        back_populates="requesting_user",
        foreign_keys=[Friend.requesting_user_id],
        lazy="selectin",
        join_depth=1
    )

    friends_received = relationship(
        "Friend",
        back_populates="target_user",
        foreign_keys=[Friend.target_user_id],
        lazy="selectin",
        join_depth=1
    )
