from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import sessionmaker, Session

from models.models import User
from services.utils import get_db

db_dependency = Annotated[Session, Depends(get_db)]


class UserRepository:
    def __init__(self, db: db_dependency):
        self.db = db

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(self):
        return self.db.query(User)


def get_all_users(db: Session = Depends(get_db())):
    return db.query(User)
