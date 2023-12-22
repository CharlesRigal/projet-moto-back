import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, String

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
