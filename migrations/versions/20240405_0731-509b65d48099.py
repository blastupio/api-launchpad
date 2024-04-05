"""auto

Revision ID: 509b65d48099
Revises: ba560db8cb95
Create Date: 2024-04-05 07:31:28.456316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '509b65d48099'
down_revision: Union[str, None] = 'ba560db8cb95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token_details', 'cliff',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE token_details SET cliff = CAST(cliff AS VARCHAR)"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token_details', 'cliff',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
