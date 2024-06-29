"""add operation reason value

Revision ID: 49707fe8417d
Revises: e522a9d71eb9
Create Date: 2024-06-29 18:48:10.659974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49707fe8417d'
down_revision: Union[str, None] = 'e522a9d71eb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE operationreason ADD VALUE IF NOT EXISTS 'AIRDROP_TASK';")


def downgrade() -> None:
    pass
