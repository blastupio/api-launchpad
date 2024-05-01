"""contract_project_id for project

Revision ID: fd4cc4ad60b2
Revises: fc9df0701eb9
Create Date: 2024-05-01 18:28:46.991504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd4cc4ad60b2'
down_revision: Union[str, None] = 'fc9df0701eb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('launchpad_project', sa.Column('contract_project_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('launchpad_project', 'contract_project_id')
    # ### end Alembic commands ###
