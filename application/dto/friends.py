from pydantic import BaseModel, Field

from models.friends import FriendsStatus


class FriendRequest(BaseModel):
    target_user_id: str = Field()


class FriendUpdateRequest(BaseModel):
    id: str = Field()
    status: FriendsStatus = Field()
