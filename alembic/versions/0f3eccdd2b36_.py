"""empty message

Revision ID: 0f3eccdd2b36
Revises: 9a590c5a6f3a
Create Date: 2024-07-15 19:49:54.916851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0f3eccdd2b36'
down_revision: Union[str, None] = '9a590c5a6f3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('company_name', sa.String(length=128), nullable=True, comment='название компании клиента'))
    op.drop_column('clients', 'company')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('company', mysql.VARCHAR(length=128), nullable=True, comment='название компании клиента'))
    op.drop_column('clients', 'company_name')
    # ### end Alembic commands ###
