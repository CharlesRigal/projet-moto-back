from sqlalchemy.orm import Session

from models.friend import FriendsStatus, Friend
from models.users import User


class FriendRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, friends: Friend):
        self.db.add(friends)
        self.db.commit()

    def update(self, friend: Friend):
        self.db.query(Friend).update({
            'id': friend.id,
            'status': friend.status
        })
        self.db.commit()

    def get_friend_by_id(self, id: str):
        return self.db.query(Friend).filter(Friend.id == id).first()

    @staticmethod
    def is_part_of_friendship(user_id: str, friend: Friend):
        if user_id == friend.target_user_id or user_id == friend.requesting_user_id:
            return True
        return False
