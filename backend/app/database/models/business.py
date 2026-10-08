from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    text,
)

from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Business(Base):
    __tablename__ = "businesses"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "code",
            name="uq_businesses_organization_code",
        ),
         UniqueConstraint(
            "id",
            "organization_id",
            name="uq_businesses_id_organization",
        ),
        CheckConstraint(
            "char_length(trim(code)) > 0",
            name="ck_businesses_code_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(name)) > 0",
            name="ck_businesses_name_not_blank",
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
            name="fk_businesses_organization_id",
        ),
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

    
