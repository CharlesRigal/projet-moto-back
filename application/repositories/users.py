from typing import List
from uuid import UUID

from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemCreateError, ItemNotInListError, SelectNotFoundError
from models.friend import FriendsStatus
from models.users import User
from services.WebsocketRegistry import WebSocketRegistry

websockets_registry = WebSocketRegistry()


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def delete_user(self, user: User) -> bool:
        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except exc.SQLAlchemyError:
            return False

    def create(self, user: User):
        try:
            self.db.add(user)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise ItemCreateError()

    def get_user_by_id(self, user_id: UUID) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise SelectNotFoundError()
        return user

    def get_user_by_username(self, username: str) -> object:
        user = self.db.query(User).filter(User.username.match(username)).first()
        if not user:
            raise SelectNotFoundError()
        return user

    def get_users_by_similar_username(self, string: str):
        search = "%{}%".format(string)
        return self.db.query(User).filter(User.username.like(search)).all()

    def get_user_by_email(self, email: str):
        user = self.db.query(User).filter(User.email.match(email)).first()
        if not user:
            raise SelectNotFoundError()
        return user

    def get_all(self):
        return self.db.query(User).all()

    @staticmethod
    def get_friends(user: User):
        friends = []
        for friend in user.friends_received:
            if friend.status == FriendsStatus.ACCEPTED:
                friends.append(friend)
        for friend in user.friends_sent:
            if friend.status == FriendsStatus.ACCEPTED:
                friends.append(friend)
        return friends

    @staticmethod
    def get_friends_as_user(user: User) -> List[User]:
        users = []
        for friend in user.friends_received:
            if friend.status == FriendsStatus.ACCEPTED:
                users.append(friend.requesting_user)
        for friend in user.friends_sent:
            if friend.status == FriendsStatus.ACCEPTED:
                users.append(friend.target_user)
        return users

    @staticmethod
    def get_connected_friends(user: User) -> List[User]:
        users = []
        for friend in user.friends_received + user.friends_sent:
            if (
                friend.status == FriendsStatus.ACCEPTED
                and websockets_registry.connection_is_active(friend.requesting_user.id)
            ):
                users.append(friend.requesting_user)
        return users

    @staticmethod
    def get_pendings_sent(user):
        friends = []
        for friend in user.friends_sent:
            if friend.status == FriendsStatus.PENDING:
                friends.append(friend)
        return friends

    @staticmethod
    def get_pendings_received(user):
        friends = []
        for friend in user.friends_received:
            if friend.status == FriendsStatus.PENDING:
                friends.append(friend)

        return friends

    @staticmethod
    def get_friend_user(user: User, user2_id: str):
        """
        verifie si l'user possede l'user2 en ami, et retourne l'objet user de user2 si oui
        """
        friends = UserRepository.get_friends(user)
        for friend in friends:
            if str(friend.requesting_user_id) == str(user2_id):
                return friend.requesting_user
            if str(friend.target_user_id) == str(user2_id):
                return friend.target_user
        raise ItemNotInListError()
