import enum
import json
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from sqlalchemy_serializer import SerializerMixin


class FriendsStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DENIED = 2
    REMOVED = 3


class Friend(Base, SerializerMixin):
    __tablename__ = 'friends'
    serialize_rules = (
        '-requesting_user.friends_sent', '-requesting_user.friends_received', '-requesting_user.routes_joined', '-requesting_user.routes_owned',  '-requesting_user.role',  '-requesting_user.email',
        '-target_user.friends_sent', '-target_user.friends_received', '-target_user.routes_joined', '-target_user.routes_owned',  '-target_user.role',  '-target_user.email'
                       )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(Enum(FriendsStatus))

    requesting_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    requesting_user = relationship(
        "User",
        foreign_keys=[requesting_user_id],
        back_populates="friends_sent",
        lazy="selectin",
        join_depth=1
    )
    target_user = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="friends_received",
        lazy="selectin",
        join_depth=1
    )

