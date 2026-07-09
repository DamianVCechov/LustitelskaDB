"""'Add Game points to Warmer game Result'

Revision ID: 8f4aa376a76e
Revises: 0543b312c75d
Create Date: 2026-07-10 01:44:08.912825

"""

# revision identifiers, used by Alembic.
revision = '8f4aa376a76e'
down_revision = '0543b312c75d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'warmer_games_results',
        sa.Column('game_points', sa.Boolean, nullable=False, index=True, default=0)
    )


def downgrade():
    op.drop_column('warmer_games_results', 'game_points')
