from pydantic import BaseModel, Field

from application.models.friend import FriendsStatus


class FriendCreateRequest(BaseModel):
    target_user_id: str = Field()


class FriendUpdateRequest(BaseModel):
    id: str = Field()
    status: FriendsStatus = Field()
