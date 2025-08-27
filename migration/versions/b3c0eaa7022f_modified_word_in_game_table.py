"""Modified word in game table

Revision ID: b3c0eaa7022f
Revises: ef73d85c02d3
Create Date: 2025-08-27 04:07:54.275664

"""

# revision identifiers, used by Alembic.
revision = 'b3c0eaa7022f'
down_revision = 'ef73d85c02d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'games',
        'word',
        type_=sa.UnicodeText(5),
        nullable=True,
        index=True
    )


def downgrade():
    op.alter_column(
        'games',
        'word',
        type_=sa.UnicodeText(5),
        nullable=False,
        index=True,
        default=''
    )
