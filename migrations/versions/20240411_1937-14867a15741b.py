"""empty message

Revision ID: 14867a15741b
Revises: 521d7a215689
Create Date: 2024-04-11 19:37:44.239105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14867a15741b'
down_revision: Union[str, None] = '521d7a215689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    connection.execute(sa.text("ALTER TABLE launchpad_project ALTER COLUMN project_type TYPE text USING project_type::text;"))
    connection.execute(sa.text("UPDATE launchpad_project SET project_type = 'PRIVATE_PRESALE' WHERE project_type = 'PARTNERSHIP_PRESALE'"))
    connection.execute(sa.text("ALTER TYPE projecttype RENAME TO projecttype_old;"))
    connection.execute(sa.text("CREATE TYPE projecttype AS ENUM ('DEFAULT', 'PRIVATE_PRESALE');"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE launchpad_project SET project_type = 'PARTNERSHIP_PRESALE' WHERE project_type = 'PRIVATE_PRESALE'"))
    connection.execute(sa.text("DROP TYPE projecttype;"))
    connection.execute(sa.text("ALTER TYPE projecttype_old RENAME TO projecttype;"))
    connection.execute(sa.text("ALTER TABLE launchpad_project ALTER COLUMN project_type TYPE projecttype USING project_type::projecttype;"))
    # ### end Alembic commands ###