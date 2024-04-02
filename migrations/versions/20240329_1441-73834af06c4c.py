"""empty message

Revision ID: 73834af06c4c
Revises: 3009b9a67a61
Create Date: 2024-03-29 14:41:59.079410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73834af06c4c'
down_revision: Union[str, None] = '3009b9a67a61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('launchpad_project', sa.Column('logo_url', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('launchpad_project', 'logo_url')
    # ### end Alembic commands ###
