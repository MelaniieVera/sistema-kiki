from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "organization_id"],
            ["businesses.id", "businesses.organization_id"],
            name="fk_categories_business_organization",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "business_id",
            "code",
            name="uq_categories_business_code",
        ),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_categories_id_organization",
        ),
        UniqueConstraint(
            "id",
            "business_id",
            "organization_id",
            name="uq_categories_id_business_organization",
        ),
        CheckConstraint(
            "char_length(trim(code))> 0",
            name="ck_categories_code_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(name)) > 0",
            name="ck_categories_name_not_blank",
        ),
        CheckConstraint(
            "display_order >= 0",
            name="ck_categories_display_order_nonnegative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )
    
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
            name="fk_categories_organization_id",
        ),
        nullable=False,
    )
    
    business_id: Mapped[UUID] = mapped_column(
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

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
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