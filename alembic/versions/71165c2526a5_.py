"""empty message

Revision ID: 71165c2526a5
Revises: 96ecd3d26f4b
Create Date: 2024-07-03 20:55:48.247337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71165c2526a5'
down_revision: Union[str, None] = '96ecd3d26f4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('company', sa.String(length=128), nullable=True, comment='название компании клиента'))
    op.add_column('clients', sa.Column('email', sa.String(length=128), nullable=True, comment='имеил клиента клиента'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'email')
    op.drop_column('clients', 'company')
    # ### end Alembic commands ###
