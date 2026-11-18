from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_extra_types.timezone_name import _is_available

class ProductVariantCreate(BaseModel):
    name: str
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    preparation_area_i: UUID
    _is_available: bool = True

class ProductCreate(BaseModel):
    category_id: UUID
    name: str
    description: Optional[str] = None
    is_activate: bool = True
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