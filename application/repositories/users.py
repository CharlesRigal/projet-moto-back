from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from models.friends import FriendsStatus
from models.users import User
from services.utils import get_db

db_dependency = Annotated[Session, Depends(get_db)]


class UserRepository:
    def __init__(self, db: db_dependency):
        self.db = db

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
    def update(self, user: User):
        self.db.query(User).update(user) # NOT TESTED !!!
        self.db.commit()


    def get_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_by_similar_username(self, string: str):
        search = "%{}%".format(string)
        return self.db.query(User).filter(User.username.like(search)).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self):
        return self.db.query(User)

    def get_friends(self, user: User):
        friends = []
        for friend in user.friendships_received:
            if friend.type == FriendsStatus.ACCEPTED:
                friends.append(friend.requesting_user)
        for friend in user.friendships_sent:
            if friend.type == FriendsStatus.ACCEPTED:
                friends.append(friend.target_user)
        return friends

    def get_pendings_sent(self, user):
        friends = []
        for friend in user.friendships_sent:
            if friend.type == FriendsStatus.PENDING:
                friends.append(friend.target_user)
        return friends

    def get_pendings_received(self, user):
        friends = []
        for friend in user.friendships_received:
            if friend.type == FriendsStatus.PENDING:
                friends.append(friend.target_user)
        return friends


def get_all_users(db: Session):
    return db.query(User).all()
