from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemCreateError, SelectNotFoundError
from models.friend import Friend


class FriendRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, friends: Friend):
        try:
            self.db.add(friends)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise ItemCreateError()

    def get_friend_by_id(self, id: str):
        friend = self.db.query(Friend).filter(Friend.id == id).first()
        if not friend:
            raise SelectNotFoundError()
        return friend

    @staticmethod
    def is_part_of_friendship(user_id: str, friend: Friend):
        if str(user_id) == str(friend.target_user_id) or str(user_id) == str(
            friend.requesting_user_id
        ):
            return True
        return False
