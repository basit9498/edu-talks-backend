"""add roadmap jsonb to ai_planner_conversations

Revision ID: 8cea1e60838e
Revises: 2fc73f4bfb35
Create Date: 2026-01-27 11:39:34.794844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cea1e60838e'
down_revision: Union[str, Sequence[str], None] = '2fc73f4bfb35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
