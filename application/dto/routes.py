from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from dto.waypoints import WayPointCreateRequest


class RouteCreateRequest(BaseModel):
    name: str = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    waypoints: Optional[List[WayPointCreateRequest]] = None
    date: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S"),
        }


class MemberAddRequest(BaseModel):
    id: str = Field()
