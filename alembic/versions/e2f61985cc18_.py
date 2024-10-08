"""empty message

Revision ID: e2f61985cc18
Revises: 25eaf42df639
Create Date: 2024-06-28 11:39:33.503513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f61985cc18'
down_revision: Union[str, None] = '25eaf42df639'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('raports_data', sa.Column('subname', sa.String(length=64), nullable=True))
    op.add_column('raports_data', sa.Column('type', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('raports_data', 'type')
    op.drop_column('raports_data', 'subname')
    # ### end Alembic commands ###
