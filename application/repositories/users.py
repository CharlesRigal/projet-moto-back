from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.general import ItemCreateError, ItemNotInListError, SelectNotFoundError
from models.friend import FriendsStatus
from models.users import User
from services.WebsocketRegistry import WebSocketRegistry

websocket_dic = WebSocketRegistry()

class UserRepository:

    async def send_friend_status(self, user: User):
        friends = self.get_friends(user)
        for friend in friends:
            friend_user = self.get_friend_user(user, friend.id)
            friend_ws = friend_user.get_connection()
            if friend_ws:
                status = "connecté" if friend_ws.open else "disconnected"
                await friend_ws.send_text(f"{user.username} was {status}")
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User):
        try:
            self.db.add(user)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ItemCreateError()


    def get_user_by_id(self, user_id: UUID):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise SelectNotFoundError()
        user.set_connection(websocket_dic.user_websocket(user.id))
        return user

    def get_user_by_username(self, username: str):
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise SelectNotFoundError()
        return user

    def get_users_by_similar_username(self, string: str):
        search = "%{}%".format(string)
        return self.db.query(User).filter(User.username.like(search)).all()

    def get_user_by_email(self, email: str):
        user = self.db.query(User).filter(User.email == email).first()
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
        friends = UserRepository.get_friends(user)
        for friend in friends:
            if str(friend.requesting_user_id) == str(user2_id):
                return friend.requesting_user
            if str(friend.target_user_id) == str(user2_id):
                return friend.target_user
        raise ItemNotInListError()
