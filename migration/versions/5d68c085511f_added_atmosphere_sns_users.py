"""Added Atmosphere SNS users

Revision ID: 5d68c085511f
Revises: b3c0eaa7022f
Create Date: 2026-07-07 23:34:49.340381

"""

# revision identifiers, used by Alembic.
revision = '5d68c085511f'
down_revision = 'b3c0eaa7022f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'atmosphere' not in tables:
        op.create_table(
                'atmosphere',
                sa.Column('uid', sa.Integer(), primary_key=True),
                sa.Column('did', sa.String(300), unique=True, nullable=False, default='', server_default=''),
                sa.Column('user_name', sa.String(255), unique=True, nullable=False, default='', server_default=''),
                sa.Column('display_name', sa.Unicode(64), nullable=True),
                sa.Column('user_info', sa.UnicodeText(), nullable=True),
                sa.Column('user_id', sa.Integer(), nullable=True),
                mysql_engine='InnoDB',
                mysql_charset='utf8mb4'
            )


def downgrade():
    op.drop_table('atmosphere')
