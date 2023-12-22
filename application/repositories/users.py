from uuid import UUID

from sqlalchemy.orm import sessionmaker, Session

from models.users import User
from services.utils import get_db


class UserRepository:
    def __init__(self):
        self.get_db = get_db

    def get_user_by_id(self, user_id: UUID):
        return self.get_db().query(User).filter(User.id == user_id).first()
