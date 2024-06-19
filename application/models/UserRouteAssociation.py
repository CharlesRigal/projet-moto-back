from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Column

from config.database import Base

class UserRouteRole(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"

class UserRouteAssociation(Base):
    __tablename__ = 'user_route_association'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'), primary_key=True)
    role = Column(UUID(as_uuid=True), Enum(UserRouteRole))
