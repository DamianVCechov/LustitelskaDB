"""Display name changed to non unique

Revision ID: a00aefdc7189
Revises: 8d930c69a0a5
Create Date: 2024-09-10 01:58:18.898177

"""

# revision identifiers, used by Alembic.
revision = 'a00aefdc7189'
down_revision = '8d930c69a0a5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_index('display_name', 'xtwitter')


def downgrade():
    op.create_index('display_name', 'xtwitter', ['display_name'], unique=True)
