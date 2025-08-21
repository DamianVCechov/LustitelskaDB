"""Added Clans

Revision ID: e35eb2537168
Revises: 0fb9d06c44cb
Create Date: 2025-08-20 23:57:26.090973

"""

# revision identifiers, used by Alembic.
revision = 'e35eb2537168'
down_revision = '0fb9d06c44cb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'clan' not in tables:
        op.create_table(
            'clan',
            sa.Column('uid', sa.Integer, primary_key=True),
            sa.Column('name', sa.Unicode(64), nullable=False, default=''),
            sa.Column('symbol', sa.Unicode(16), nullable=False, default=''),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )

    if 'clan_members' not in tables:
        op.create_table(
            'clan_members',
            sa.Column('uid', sa.Integer, primary_key=True),
            sa.Column('clan_id', sa.Integer, sa.ForeignKey('clan.uid'), index=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('tg_user.user_id'), index=True),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )


def downgrade():
    op.drop_table('clan_members')
    op.drop_table('clan')
