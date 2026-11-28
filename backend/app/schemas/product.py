from decimal import Decimal
from typing import Annotated, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


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
    variant: Optional[ProductVariantCreate] = None
    variants: Optional[list[ProductVariantCreate]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_presentations(self):
        if (self.variant is None) == (self.variants is None):
            raise ValueError("Provide either variant or variants")
        return self

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


class CatalogVariantRead(ProductVariantRead):
    preparation_area_id: Optional[UUID] = None


class CatalogProductRead(BaseModel):
    id: UUID
    category_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool
    variants: list[CatalogVariantRead]


class CatalogPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def reject_explicit_nulls(self):
        for field in self.model_fields_set - {"description"}:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProductVariantPatch(CatalogPatch):
    id: UUID
    name: Optional[ProductName] = None
    price: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    preparation_area_id: Optional[UUID] = None
    is_available: Optional[bool] = None


class NewCatalogVariant(ProductVariantCreate):
    model_config = ConfigDict(extra="forbid")


class ProductPatch(CatalogPatch):
    category_id: Optional[UUID] = None
    name: Optional[ProductName] = None
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None
    variant: Optional[ProductVariantPatch] = None

    variants: Optional[list[Union[ProductVariantPatch, NewCatalogVariant]]] = Field(
        default=None, min_length=1
    )

    @model_validator(mode="after")
    def check_presentations(self):
        if self.variant is not None and self.variants is not None:
            raise ValueError("Provide either variant or variants")
        ids = [item.id for item in self.variants or [] if isinstance(item, ProductVariantPatch)]
        if len(set(ids)) != len(ids):
            raise ValueError("Each variant can only be patched once")
        return self
