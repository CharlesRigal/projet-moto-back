from pydantic import BaseModel
from uuid import UUID

class UpdateEditionRequest(BaseModel):
    user_id: UUID
    route_id: UUID
    edition: bool
