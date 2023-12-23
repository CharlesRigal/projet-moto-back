import uuid as uuid_pkg

from sqlalchemy import Column, String, Integer

from config.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    # username = Column(String(254), unique=True)
    # email = Column(String(254), unique=True)
    # password = Column(String(254))
    # auth0_id = Column(String(254), unique=True)
# TODO: Add self relation for friend list
