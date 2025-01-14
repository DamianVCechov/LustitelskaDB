"""Added wednesday challenge words table

Revision ID: e09a86ac2731
Revises: a00aefdc7189
Create Date: 2025-01-13 18:14:26.546907

"""

# revision identifiers, used by Alembic.
revision = 'e09a86ac2731'
down_revision = 'a00aefdc7189'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'wednesday_challenge_words' not in tables:
        op.create_table(
            'wednesday_challenge_words',
            sa.Column('uid', sa.Integer, primary_key=True),
            sa.Column('xtwitter_uid', sa.Integer, sa.ForeignKey('xtwitter.uid'), index=True),
            sa.Column('game_no', sa.Integer, nullable=False, index=True, default=0),
            sa.Column('first_word', sa.Unicode(5), nullable=False, index=True, default=''),
            sa.Column('second_word', sa.Unicode(5), nullable=False, index=True, default=''),
            sa.Column('third_word', sa.Unicode(5), nullable=False, index=True, default=''),
            sa.Column('comment', sa.UnicodeText, nullable=True),
            sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now()),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )

def downgrade():
    op.drop_table('wednesday_challenge_words')
