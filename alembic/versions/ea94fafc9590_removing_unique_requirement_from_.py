"""Removing unique requirement from article column in oddpub_metrics table

Revision ID: ea94fafc9590
Revises: b751c4aa2a6e
Create Date: 2025-01-30 09:01:04.492792

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea94fafc9590"
down_revision: Union[str, None] = "b751c4aa2a6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        op.f("ix_oddpub_metrics_article"), table_name="oddpub_metrics"
    )


def downgrade() -> None:

    op.create_index(
        op.f("ix_oddpub_metrics_article"),
        "oddpub_metrics",
        ["article"],
        unique=True,
    )
