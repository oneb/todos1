"""Add in_progress state

Revision ID: 5f006ca5efeb
Revises: 9889cd64c84b
Create Date: 2025-03-19 04:23:20.794599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f006ca5efeb'
down_revision: Union[str, None] = '9889cd64c84b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER TABLE for changing column types
    # Create a new temporary table with the updated schema
    with op.batch_alter_table('tasks') as batch_op:
        # Create the new enum type
        batch_op.drop_column('state')
        batch_op.add_column(sa.Column('state', sa.Enum('TODO', 'IN_PROGRESS', 'DONE', name='taskstate'), nullable=True))
        
        # Set default state for any existing records to 'TODO'
        op.execute("UPDATE tasks SET state = 'TODO' WHERE state IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # SQLite doesn't support ALTER TABLE for changing column types
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.drop_column('state')
        batch_op.add_column(sa.Column('state', sa.VARCHAR(length=4), nullable=True))
        
        # Map IN_PROGRESS back to TODO in the downgrade
        op.execute("UPDATE tasks SET state = 'TODO' WHERE state = 'IN_PROGRESS'")
        op.execute("UPDATE tasks SET state = 'DONE' WHERE state = 'DONE'")
