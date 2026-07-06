"""update the discussion table add col is_deleted

Revision ID: 049b6e412297
Revises: 43126a02e8f1
Create Date: 2025-12-25 13:16:42.270574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '049b6e412297'
down_revision: Union[str, Sequence[str], None] = '43126a02e8f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
