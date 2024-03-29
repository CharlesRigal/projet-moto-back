from decimal import Decimal
from pydantic import BaseModel, Field


class WayPointCreateRequest(BaseModel):
    latitude: Decimal = Field(decimal_places=6, le=90, ge=-90)
    longitude: Decimal = Field(decimal_places=6, le=180, ge=-180)
    name: str = Field(max_length=100)
    order: int = Field(ge=0)
