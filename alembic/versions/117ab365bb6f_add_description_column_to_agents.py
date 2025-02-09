"""Add description column to agents

Revision ID: 117ab365bb6f
Revises: 9a779217f20c
Create Date: 2025-02-09 05:36:48.613656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '117ab365bb6f'
down_revision: Union[str, None] = '9a779217f20c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('agents', sa.Column('ocs', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('agents', 'ocs')
    # ### end Alembic commands ###
