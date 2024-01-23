import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, UUID, Enum, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base


class FriendsStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DENIED = 2
    REMOVED = 3


class Friend(Base):
    __tablename__ = 'friends'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(Enum(FriendsStatus))

    requesting_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    requesting_user = relationship(
        "User",
        foreign_keys=[requesting_user_id],
        back_populates="friends_sent",
    )
    target_user = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="friends_received",
    )

