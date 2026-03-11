"""start adding users

Revision ID: d1f51adc3923
Revises: 58396348228f
Create Date: 2026-03-07 21:50:37.036134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1f51adc3923'
down_revision: Union[str, Sequence[str], None] = '58396348228f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'uq_users_email_lower',
        'users',
        [sa.literal_column('lower(email)')],
        unique=True,
    )
    op.create_table(
        'oauth_accounts',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=128), nullable=False),
        sa.Column('provider_user_id', sa.String(length=256), nullable=False),
        sa.Column('provider_email', sa.String(length=254), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_oauth_user_provider'),
    )
    op.create_index(
        'idx_oauth_user_provider',
        'oauth_accounts',
        ['user_id', 'provider'],
        unique=False,
    )
    op.add_column('habits', sa.Column('owner_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_habits_owner_id'), 'habits', ['owner_id'], unique=False)
    op.create_foreign_key(
        'fk_habits_owner_id_users',
        'habits',
        'users',
        ['owner_id'],
        ['id'],
        ondelete='CASCADE',
    )
    op.add_column('tasks', sa.Column('owner_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_tasks_owner_id'), 'tasks', ['owner_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_owner_id_users',
        'tasks',
        'users',
        ['owner_id'],
        ['id'],
        ondelete='CASCADE',
    )
    op.add_column('themes', sa.Column('owner_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_themes_owner_id'), 'themes', ['owner_id'], unique=False)
    op.create_foreign_key(
        'fk_themes_owner_id_users',
        'themes',
        'users',
        ['owner_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_themes_owner_id_users', 'themes', type_='foreignkey')
    op.drop_index(op.f('ix_themes_owner_id'), table_name='themes')
    op.drop_column('themes', 'owner_id')
    op.drop_constraint('fk_tasks_owner_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_owner_id'), table_name='tasks')
    op.drop_column('tasks', 'owner_id')
    op.drop_constraint('fk_habits_owner_id_users', 'habits', type_='foreignkey')
    op.drop_index(op.f('ix_habits_owner_id'), table_name='habits')
    op.drop_column('habits', 'owner_id')
    op.drop_index('idx_oauth_user_provider', table_name='oauth_accounts')
    op.drop_table('oauth_accounts')
    op.drop_index('uq_users_email_lower', table_name='users')
    op.drop_table('users')
