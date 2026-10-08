from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    String,
    DateTime,
    Index,
    text,
    func,
)

from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        
        CheckConstraint(
            "char_length(trim(username)) > 0",
            name="ck_user_username_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(first_name)) > 0",
            name="ck_user_first_name_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(last_name)) > 0",
            name="ck_user_last_name_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(password_hash)) > 0",
            name="ck_user_password_hash_not_blank",
        ),
        CheckConstraint(
            "email IS NULL OR char_length(trim(email)) > 0",
            name="ck_user_email_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

Index(
    "ux_users_username_ci",
    func.lower(User.username),
    unique=True,
)

Index(
    "ux_users_email_ci",
    func.lower(User.email),
    unique=True,
)