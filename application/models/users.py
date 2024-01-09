import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from models.friendship import Friendship, FriendShipStatus


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default="user")

    friendships_sent = relationship(
        "Friendship",
        back_populates="requesting_user",
        foreign_keys=[Friendship.requesting_user_id]
    )
    friendships_received = relationship(
        "Friendship",
        back_populates="target_user",
        foreign_keys=[Friendship.target_user_id]
    )

    def get_friends(self):
        friends = []
        for friend in self.friendships_received:
            if friend.type == FriendShipStatus.ACCEPTED:
                friends.append(friend.requesting_user)
        for friend in self.friendships_sent:
            if friend.type == FriendShipStatus.ACCEPTED:
                friends.append(friend.target_user)
        return friends

    def get_pendings_sent(self):
        friends = []
        for friend in self.friendships_sent:
            if friend.type == FriendShipStatus.PENDING:
                friends.append(friend.target_user)
        return friends

    def get_pendings_received(self):
        friends = []
        for friend in self.friendships_received:
            if friend.type == FriendShipStatus.PENDING:
                friends.append(friend.target_user)
        return friends
