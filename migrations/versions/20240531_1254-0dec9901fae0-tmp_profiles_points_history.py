"""tmp profiles, points history

Revision ID: 0dec9901fae0
Revises: f9ada84a0365
Create Date: 2024-05-31 12:54:56.464147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0dec9901fae0'
down_revision: Union[str, None] = 'f9ada84a0365'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_profiles_address', table_name='profiles')
    op.drop_constraint("points_history_profile_id_fkey", table_name='points_history')
    op.drop_table('profiles')
    op.drop_table('points_history')
    op.create_table('tmp_profiles',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('points', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), server_default=sa.text('0::bigint'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tmp_profiles_address'), 'tmp_profiles', ['address'], unique=True)
    op.create_table('tmp_points_history',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('operation_type', sa.Enum('ADD', 'ADD_REF', 'ADD_REF_BONUS', 'ADD_SYNC', 'ADD_REF_SYNC', 'ADD_EXTRA', 'ADD_MANUAL', 'ADD_IDO_POINTS', name='operationtype'), nullable=False),
    sa.Column('points_before', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), server_default=sa.text('0::bigint'), nullable=False),
    sa.Column('amount', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), server_default=sa.text('0::bigint'), nullable=False),
    sa.Column('points_after', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), server_default=sa.text('0::bigint'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('profile_id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['tmp_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tmp_points_history')
    op.drop_index(op.f('ix_tmp_profiles_address'), table_name='tmp_profiles')
    op.drop_table('tmp_profiles')
    op.execute("DROP TYPE operationtype")
    op.create_table('profiles',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('address', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('points', sa.BIGINT(), server_default=sa.text('(0)::bigint'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='profiles_pkey')
    )
    op.create_table('points_history',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('operation_type', postgresql.ENUM('ADD', 'ADD_REF', 'ADD_REF_BONUS', 'ADD_SYNC', 'ADD_REF_SYNC', 'ADD_EXTRA', 'ADD_MANUAL', 'ADD_IDO_POINTS', name='operationtype'), autoincrement=False, nullable=False),
    sa.Column('points_before', sa.BIGINT(), server_default=sa.text('(0)::bigint'), autoincrement=False, nullable=False),
    sa.Column('amount', sa.BIGINT(), server_default=sa.text('(0)::bigint'), autoincrement=False, nullable=False),
    sa.Column('points_after', sa.BIGINT(), server_default=sa.text('(0)::bigint'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('profile_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], name='points_history_profile_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='points_history_pkey')
    )

    op.create_index('ix_profiles_address', 'profiles', ['address'], unique=True)

    # ### end Alembic commands ###
