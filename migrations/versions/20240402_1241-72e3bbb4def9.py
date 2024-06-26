"""auto

Revision ID: 72e3bbb4def9
Revises: 1308fc4fe056
Create Date: 2024-04-02 12:41:44.926309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72e3bbb4def9'
down_revision: Union[str, None] = '1308fc4fe056'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('launchpad_project', 'id',
               existing_type=sa.BIGINT(),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('launchpad_project', 'id',
               existing_type=sa.String(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###
