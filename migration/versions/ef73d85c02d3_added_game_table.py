"""Added game table

Revision ID: ef73d85c02d3
Revises: e35eb2537168
Create Date: 2025-08-24 19:10:11.452886

"""

# revision identifiers, used by Alembic.
revision = 'ef73d85c02d3'
down_revision = 'e35eb2537168'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'games' not in tables:
        op.create_table(
            'games',
            sa.Column('uid', sa.Integer, primary_key=True),
            sa.Column('game_no', sa.Integer, nullable=False, unique=True, default=0),
            sa.Column('word', sa.Unicode(5), nullable=False, index=True, default=''),
            sa.Column('post_xid', sa.String(20), nullable=True),
            sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now()),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )


def downgrade():
    op.drop_table('games')
