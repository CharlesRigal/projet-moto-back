from typing import Optional, List

from pydantic import BaseModel, Field

from application.dto.waypoints import WayPointCreateRequest


class RouteCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(default=None, min_length=5, max_length=500)
    waypoints: List[WayPointCreateRequest]


class MemberAddRequest(BaseModel):
    id: str = Field()
