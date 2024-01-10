import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from models.friends import Friends, FriendsStatus


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default="user")

    friends_sent = relationship(
        "Friends",
        back_populates="requesting_user",
        foreign_keys=[Friends.requesting_user_id]
    )
    friends_received = relationship(
        "Friends",
        back_populates="target_user",
        foreign_keys=[Friends.target_user_id]
    )





