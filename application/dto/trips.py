from typing import Optional

from pydantic import BaseModel, Field


class TripCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(default=None, min_length=5, max_length=500)
