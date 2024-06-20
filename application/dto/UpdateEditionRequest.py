from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class UpdateEditionRequest(BaseModel):
    user_id: UUID
    route_id: Optional[UUID] = None
    edition: bool
