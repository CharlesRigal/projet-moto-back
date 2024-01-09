import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base


class User(Base):
    __tablename__ = 'users'
    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username: str = Column(String(30), unique=True)
    email: str = Column(String(100), unique=True)
    hashed_password: str = Column(String(254))
    is_active: bool = Column(Boolean, default=True)
    role: str = Column(String(30), default="user")

    friendships_sent = relationship("Friendship", back_populates="users")
    friendships_received = relationship("Friendship", back_populates="users")



class FriendShipStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DENIED = 2
    REMOVED = 3


class Friendship(Base):
    __tablename__ = 'friendships'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(Enum(FriendShipStatus))

    requesting_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    requesting_user = relationship(
        "User", foreign_keys=[requesting_user_id], back_populates="friendships_sent"
    )
    target_user = relationship(
        "User", foreign_keys=[target_user_id], back_populates="friendships_received"
    )

    users = relationship("User", back_populates="friendships")
