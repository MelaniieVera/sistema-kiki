from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    display_order: int
    is_active: bool
