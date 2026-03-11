"""add theme owner/name uniqueness

Revision ID: 1ee7d6fca58f
Revises: 5c4a2820a5f7
Create Date: 2026-03-11 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1ee7d6fca58f'
down_revision: Union[str, Sequence[str], None] = '5c4a2820a5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'uq_themes_owner_id_name',
        'themes',
        ['owner_id', 'name'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_themes_owner_id_name', 'themes', type_='unique')
