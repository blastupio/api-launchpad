"""add history blp stake

Revision ID: 1a6f76d1a76c
Revises: 735ddcd5677a
Create Date: 2024-06-19 11:30:14.820861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1a6f76d1a76c'
down_revision: Union[str, None] = '735ddcd5677a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE operationreason ADD VALUE IF NOT EXISTS 'BLP_STAKING';")
    op.execute("ALTER TYPE operationtype ADD VALUE IF NOT EXISTS 'ADD_BLP_STAKING_POINTS';")

    op.create_table('stake_blp_history',
    sa.Column('id', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('type', sa.Enum('UNSTAKE', 'STAKE', 'CLAIM_REWARDS', name='historyblpstaketype'), nullable=False),
    sa.Column('amount', sa.Text(), nullable=False),
    sa.Column('user_address', sa.String(), nullable=False),
    sa.Column('pool_id', sa.Integer(), nullable=False),
    sa.Column('chain_id', sa.String(), nullable=False),
    sa.Column('txn_hash', sa.String(), nullable=True),
    sa.Column('block_number', sa.BigInteger().with_variant(sa.BIGINT(), 'postgresql').with_variant(sa.INTEGER(), 'sqlite'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('txn_hash', name='ux_stake_blp_history_txn_hash')
    )
    op.create_index(op.f('ix_stake_blp_history_user_address'), 'stake_blp_history', ['user_address'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stake_blp_history_user_address'), table_name='stake_blp_history')
    op.drop_constraint("ux_stake_blp_history_txn_hash", table_name='stake_blp_history')
    op.drop_table('stake_blp_history')
    op.execute("DROP TYPE historyblpstaketype")
    # ### end Alembic commands ###
