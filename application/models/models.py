import uuid as uuid_pkg

from sqlalchemy import Column, String, Integer, Boolean

from config.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String(254))
    is_active = Column(Boolean, default=True)
    role = Column(String)
# TODO: Add self relation for friend list
