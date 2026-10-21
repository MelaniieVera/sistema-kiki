"""add category display order

Revision ID: 408edddf20bb
Revises: 3f0c84fc0b51
Create Date: 2026-10-20 08:44:10.391421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '408edddf20bb'
down_revision: Union[str, Sequence[str], None] = '3f0c84fc0b51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'categories',
        sa.Column(
            'display_order',
            sa.Integer(),
            server_default=sa.text('0'),
            nullable=False
        )
    )

    op.create_check_constraint(
        'ck_categories_display_order_nonnegative',
        'categories',
        'display_order >= 0'
    )


def downgrade() -> None:
    op.drop_constraint(
        'ck_categories_display_order_nonnegative',
        'categories',
        type_='check'
    )

    op.drop_column(
        'categories',
        'display_order'
    )