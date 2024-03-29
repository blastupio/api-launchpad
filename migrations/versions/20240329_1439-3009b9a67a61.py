"""empty message

Revision ID: 3009b9a67a61
Revises: 4d4d74d067de
Create Date: 2024-03-29 14:39:35.332594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3009b9a67a61'
down_revision: Union[str, None] = '4d4d74d067de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_image',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('project_id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['launchpad_project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_link',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('DEFAULT', 'TWITTER', 'DISCORD', 'TELEGRAM', name='projectlinktype'), server_default='DEFAULT', nullable=True),
    sa.Column('project_id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['launchpad_project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('link')
    op.drop_table('file')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('project_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['launchpad_project.id'], name='file_project_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='file_pkey')
    )
    op.create_table('link',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('project_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['launchpad_project.id'], name='link_project_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='link_pkey')
    )
    op.drop_table('project_link')
    op.drop_table('project_image')
    # ### end Alembic commands ###