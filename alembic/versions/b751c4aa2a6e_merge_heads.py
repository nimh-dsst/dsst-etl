"""merge heads

Revision ID: b751c4aa2a6e
Revises: 0b2196c1c66b, 600039d1785e
Create Date: 2025-01-30 08:59:15.317385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b751c4aa2a6e'
down_revision: Union[str, None] = ('0b2196c1c66b', '600039d1785e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
