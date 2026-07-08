"""Added Warmer Game model

Revision ID: 8059f6120ba3
Revises: 5d68c085511f
Create Date: 2026-07-08 22:45:29.419634

"""

# revision identifiers, used by Alembic.
revision = '8059f6120ba3'
down_revision = '5d68c085511f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'warmer_games' not in tables:
        op.create_table(
                'warmer_games',
                sa.Column('uid', sa.Integer(), primary_key=True),
                sa.Column('game_date', sa.Date, nullable=False, unique=True, default=sa.func.now(), server_default=sa.func.now()),
                sa.Column('word', sa.Unicode(32), nullable=True, index=True),
                sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
                sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now()),
                mysql_engine='InnoDB',
                mysql_charset='utf8mb4'
            )

    if 'warmer_games_results' not in tables:
        op.create_table(
                'warmer_games_results',
                sa.Column('uid', sa.Integer(), primary_key=True),
                sa.Column('user_id', sa.Integer, sa.ForeignKey('tg_user.user_id'), index=True),
                sa.Column('game_date', sa.Date, nullable=False, index=True, default=sa.func.now(), server_default=sa.func.now()),
                sa.Column('game_guesses', sa.SmallInteger, nullable=True, index=True),
                sa.Column('comment', sa.UnicodeText, nullable=True),
                sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
                sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now()),
                mysql_engine='InnoDB',
                mysql_charset='utf8mb4'
            )

def downgrade():
    op.drop_table('warmer_games')
    op.drop_table('warmer_games_results')
