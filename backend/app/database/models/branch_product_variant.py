from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BranchProductVariant(Base):
    __tablename__ = "branch_product_variants"

    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "business_id", "organization_id"],
            [
                "branches.id",
                "branches.business_id",
                "branches.organization_id",
            ],
            name="fk_branch_product_variants_branch_business_organization",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["product_variant_id", "business_id", "organization_id"],
            [
                "product_variants.id",
                "product_variants.business_id",
                "product_variants.organization_id",
            ],
            name="fk_branch_product_variants_variant_business_organization",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["preparation_area_id", "branch_id", "organization_id"],
            [
                "preparation_areas.id",
                "preparation_areas.branch_id",
                "preparation_areas.organization_id",
            ],
            name="fk_branch_product_variants_preparation_area_branch",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "branch_id",
            "product_variant_id",
            name="uq_branch_product_variants_branch_variant",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_branch_product_variants_price_nonnegative",
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

    branch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )

    product_variant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )

    preparation_area_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    is_available: Mapped[bool] = mapped_column(
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