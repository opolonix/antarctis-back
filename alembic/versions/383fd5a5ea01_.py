"""empty message

Revision ID: 383fd5a5ea01
Revises: 716027b5bbd9
Create Date: 2024-07-15 19:58:25.575703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '383fd5a5ea01'
down_revision: Union[str, None] = '716027b5bbd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('last_activity', sa.DateTime(), nullable=True, comment='дата последней активности клиента'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'last_activity')
    # ### end Alembic commands ###
