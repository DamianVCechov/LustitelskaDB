"""Initial scheme

Revision ID: da0888f6a8ae
Revises: None
Create Date: 2024-08-24 23:28:08.104273

"""

# revision identifiers, used by Alembic.
revision = 'da0888f6a8ae'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'libriciphers' not in tables:
        op.create_table(
            'libriciphers',
            sa.Column('uid', sa.Integer, autoincrement=True, primary_key=True),
            sa.Column('part', sa.Integer, nullable=False, index=True, default=0),
            sa.Column('question', sa.Unicode(100), nullable=False, default=""),
            sa.Column('description', sa.UnicodeText(2 ** 32 - 1)),
            sa.Column('answer', sa.UnicodeText(2 ** 32 - 1)),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )


def downgrade():
    pass
