import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum

from config.database import Base


class User(Base):
    __tablename__ = 'users'
    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username: str = Column(String(30), unique=True)
    email: str = Column(String(100), unique=True)
    hashed_password: str = Column(String(254))
    is_active: bool = Column(Boolean, default=True)
    role: str = Column(String(30), default="user")


class FriendShipStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DENIED = 2
    REMOVED = 3


class Friendship(Base):
    __tablename__ = 'friendships'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_user1 = Column(UUID(as_uuid=True))
    id_user2 = Column(UUID(as_uuid=True))
    status = Column(Enum(FriendShipStatus))
