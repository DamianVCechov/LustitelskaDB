"""'Add Game Rank for Warmer game Result'

Revision ID: 0543b312c75d
Revises: 8059f6120ba3
Create Date: 2026-07-10 00:31:22.461799

"""

# revision identifiers, used by Alembic.
revision = '0543b312c75d'
down_revision = '8059f6120ba3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'warmer_games_results',
        sa.Column('game_rank', sa.Boolean, nullable=True, default=True)
    )


def downgrade():
    op.drop_column('warmer_games_results', 'game_rank')
