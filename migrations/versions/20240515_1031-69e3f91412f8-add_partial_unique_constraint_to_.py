"""Add partial unique constraint to LaunchpadContractEvents

Revision ID: 69e3f91412f8
Revises: edd95b89a2d9
Create Date: 2024-05-15 10:31:42.834148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69e3f91412f8'
down_revision: Union[str, None] = 'edd95b89a2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('_user_contract_event_uc', 'launchpad_contract_events', ['user_address', 'contract_project_id', 'event_type'], unique=True, postgresql_where=sa.text("event_type = 'USER_REGISTERED'"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('_user_contract_event_uc', table_name='launchpad_contract_events', postgresql_where=sa.text("event_type = 'USER_REGISTERED'"))
    # ### end Alembic commands ###
