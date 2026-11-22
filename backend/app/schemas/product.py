from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints


ProductName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=125)
]


class ProductVariantCreate(BaseModel):
    name: ProductName
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    preparation_area_id: UUID
    is_available: bool = True

class ProductCreate(BaseModel):
    category_id: UUID
    name: ProductName
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = True
    variant: ProductVariantCreate

class ProductVariantRead(BaseModel):
    id: UUID
    code: str
    name: str
    price: Decimal
    preparation_area_id: UUID
    is_available: bool


class ProductRead(BaseModel):
    id: UUID
    category_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool
    variant: ProductVariantRead
