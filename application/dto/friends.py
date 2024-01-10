from pydantic import BaseModel, Field


class FriendRequest(BaseModel):
    target_user_id: str = Field()
