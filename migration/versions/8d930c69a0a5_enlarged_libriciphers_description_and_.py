"""Enlarged LibriCiphers description and answer cols

Revision ID: 8d930c69a0a5
Revises: da0888f6a8ae
Create Date: 2024-08-24 23:28:27.740652

"""

# revision identifiers, used by Alembic.
revision = '8d930c69a0a5'
down_revision = 'da0888f6a8ae'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'libriciphers',
        'description',
        type_=sa.UnicodeText(2 ** 32 - 1)
    )
    op.alter_column(
        'libriciphers',
        'answer',
        type_=sa.UnicodeText(2 ** 23 - 1)
    )


def downgrade():
    op.alter_column(
        'libriciphers',
        'answer',
        type_=sa.UnicodeText
    )
    op.alter_column(
        'libriciphers',
        'description',
        type_=sa.UnicodeText
    )
