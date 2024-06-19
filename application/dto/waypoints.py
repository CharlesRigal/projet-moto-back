from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WayPointCreateRequest(BaseModel):
    latitude: Decimal = Field(decimal_places=6, le=90, ge=-90)
    longitude: Decimal = Field(decimal_places=6, le=180, ge=-180)
    name: str = Field(max_length=100)
    order: Optional[int] = None
    user_id: Optional[str] = None
