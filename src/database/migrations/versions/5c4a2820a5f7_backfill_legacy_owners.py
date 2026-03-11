"""backfill legacy owners

Revision ID: 5c4a2820a5f7
Revises: d1f51adc3923
Create Date: 2026-03-11 13:30:00.000000

"""
from datetime import UTC, datetime
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


LEGACY_OWNER_EMAIL = 'legacy-owner@habitflow.invalid'
OWNED_TABLES = ('habits', 'tasks', 'themes')


# revision identifiers, used by Alembic.
revision: str = '5c4a2820a5f7'
down_revision: Union[str, Sequence[str], None] = 'd1f51adc3923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    legacy_owner_id = uuid4()
    now = datetime.now(UTC)

    op.execute(
        sa.text(
            """
            INSERT INTO users (id, email, password_hash, is_active, created_at, updated_at)
            VALUES (:id, :email, :password_hash, :is_active, :created_at, :updated_at)
            """
        ).bindparams(
            id=legacy_owner_id,
            email=LEGACY_OWNER_EMAIL,
            password_hash=None,
            is_active=False,
            created_at=now,
            updated_at=now,
        )
    )

    for table_name in OWNED_TABLES:
        op.execute(
            sa.text(
                f'UPDATE {table_name} SET owner_id = :owner_id WHERE owner_id IS NULL'
            ).bindparams(owner_id=legacy_owner_id)
        )
        op.alter_column(
            table_name,
            'owner_id',
            existing_type=sa.UUID(),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table_name in reversed(OWNED_TABLES):
        op.alter_column(
            table_name,
            'owner_id',
            existing_type=sa.UUID(),
            nullable=True,
        )
        op.execute(
            sa.text(
                f'''
                UPDATE {table_name}
                SET owner_id = NULL
                WHERE owner_id = (
                    SELECT id
                    FROM users
                    WHERE email = :email
                )
                '''
            ).bindparams(email=LEGACY_OWNER_EMAIL)
        )

    op.execute(
        sa.text('DELETE FROM users WHERE email = :email').bindparams(
            email=LEGACY_OWNER_EMAIL
        )
    )
