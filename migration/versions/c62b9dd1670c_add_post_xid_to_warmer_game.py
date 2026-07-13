"""'Add  post_xid to Warmer Game'

Revision ID: c62b9dd1670c
Revises: 8f4aa376a76e
Create Date: 2026-07-13 22:18:46.604022

"""

# revision identifiers, used by Alembic.
revision = 'c62b9dd1670c'
down_revision = '8f4aa376a76e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'warmer_games',
        sa.Column('post_xid', sa.String(20), nullable=True)
    )

def downgrade():
    op.drop_column('warmer_games', 'game_rank')
