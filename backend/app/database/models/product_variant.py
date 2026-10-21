from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"

    __table_args__ = (
        ForeignKeyConstraint(
            ["product_id", "business_id", "organization_id"],
            [
                "products.id",
                "products.business_id",
                "products.organization_id",
            ],
            name="fk_product_variants_product_business_organization",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "product_id",
            "code",
            name="uq_product_variants_product_code",
        ),
        UniqueConstraint(
            "business_id",
            "sku",
            name="uq_product_variants_business_sku",
        ),
        UniqueConstraint(
            "id",
            "business_id",
            "organization_id",
            name="uq_product_variants_id_business_organization",
        ),
        CheckConstraint(
            "char_length(trim(code)) > 0",
            name="ck_product_variants_code_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(name)) > 0",
            name="ck_product_variants_name_not_blank",
        ),
        CheckConstraint(
            "sku IS NULL OR char_length(trim(sku)) > 0",
            name="ck_product_variants_sku_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )
    
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    
    business_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
    name: Mapped[str] = mapped_column(
        String(125),
        nullable=False,
    )
    
    sku: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
