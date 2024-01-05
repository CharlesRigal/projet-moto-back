import uuid
import uuid as uuid_pkg

from sqlalchemy import Column, String, Integer, Boolean, UUID

from config.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(30), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String(30), default="user")
# TODO: Add self relation for friend list
