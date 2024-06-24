"""add operation reason blastbox buy

Revision ID: 735ddcd5677a
Revises: 98c3e5267e08
Create Date: 2024-06-14 18:40:51.849972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '735ddcd5677a'
down_revision: Union[str, None] = '98c3e5267e08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE operationreason ADD VALUE IF NOT EXISTS 'BLASTBOX_BUY';")


def downgrade() -> None:
    pass
