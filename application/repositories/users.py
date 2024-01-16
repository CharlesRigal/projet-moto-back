from sqlalchemy.orm import Session

from models.friend import FriendsStatus
from models.users import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()

    def update(self, user: User):
        self.db.query(User).update(user)  # NOT TESTED !!!
        self.db.commit()

    def get_user_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_users_by_similar_username(self, string: str):
        search = "%{}%".format(string)
        return self.db.query(User).filter(User.username.like(search)).all()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self):
        return self.db.query(User).all()

    @staticmethod
    def get_friends(user: User):
        friends = []
        for friend in user.friends_received:
            if friend.status == FriendsStatus.ACCEPTED:
                friends.append(friend.requesting_user)
        for friend in user.friends_sent:
            if friend.status == FriendsStatus.ACCEPTED:
                friends.append(friend.target_user)
        return friends

    @staticmethod
    def get_pendings_sent(user):
        friends = []
        for friend in user.friends_sent:
            if friend.status == FriendsStatus.PENDING:
                friends.append(friend.target_user)
        return friends

    @staticmethod
    def get_pendings_received(user):
        friends = []
        for friend in user.friends_received:
            if friend.status == FriendsStatus.PENDING:
                friends.append(friend.requesting_user)

        return friends

    @staticmethod
    def get_friend(user: User, user2_id: str):
        friends = UserRepository.get_friends(user)
        for friend in friends:
            if str(friend.id) == user2_id:
                return friend
        return None
