from uuid import UUID
from pydantic import BaseModel, ConfigDict

class PreparationAreaRead (BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    is_active: bool