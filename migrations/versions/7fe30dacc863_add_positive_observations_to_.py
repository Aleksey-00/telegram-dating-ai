"""add positive observations to conversation assessments

Revision ID: 7fe30dacc863
Revises: ef1ce0f60850
Create Date: 2026-08-18 13:00:05.197280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7fe30dacc863"
down_revision: Union[str, Sequence[str], None] = "ef1ce0f60850"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "conversation_assessments",
        sa.Column(
            "positive_observations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "conversation_assessments",
        "positive_observations",
    )
