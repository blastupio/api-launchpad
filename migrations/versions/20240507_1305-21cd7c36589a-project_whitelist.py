"""project whitelist

Revision ID: 21cd7c36589a
Revises: 6cfeb4e97938
Create Date: 2024-05-07 13:05:36.777050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21cd7c36589a'
down_revision: Union[str, None] = '6cfeb4e97938'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_whitelist',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('user_address', sa.String(), nullable=False),
    sa.Column('project_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['launchpad_project.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'user_address', name='uc_project_id_user_address')
    )
    op.create_index(op.f('ix_project_whitelist_user_address'), 'project_whitelist', ['user_address'], unique=False)
    op.add_column('launchpad_project', sa.Column('kys_required', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('launchpad_project', sa.Column('whitelist_required', sa.Boolean(), server_default='false', nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('launchpad_project', 'whitelist_required')
    op.drop_column('launchpad_project', 'kys_required')
    op.drop_index(op.f('ix_project_whitelist_user_address'), table_name='project_whitelist')
    op.drop_constraint("uc_project_id_user_address", "project_whitelist")
    op.drop_table('project_whitelist')
    # ### end Alembic commands ###