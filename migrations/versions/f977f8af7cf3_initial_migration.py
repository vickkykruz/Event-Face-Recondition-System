"""Initial migration

Revision ID: f977f8af7cf3
Revises: 149f87b4fbaa
Create Date: 2025-02-16 16:30:23.756217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f977f8af7cf3'
down_revision: Union[str, None] = '149f87b4fbaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('students', sa.Column('face_encoding', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('students', 'face_encoding')
    # ### end Alembic commands ###
