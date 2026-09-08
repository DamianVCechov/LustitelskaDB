"""'Added Warmer game result screenshots table'

Revision ID: a12f3e8d3ce6
Revises: c62b9dd1670c
Create Date: 2026-09-07 04:32:55.588213

"""

# revision identifiers, used by Alembic.
revision = 'a12f3e8d3ce6'
down_revision = 'c62b9dd1670c'

from alembic import op
import sqlalchemy as sa
from tgext.datahelpers.fields import Attachment, AttachedImage


class ScreenShotAttachedImage(AttachedImage):
    thumbnail_size = (320, 320)
    thumbnail_format = 'webp'


def upgrade():
    conn = op.get_bind()
    inspector = sa.engine.reflection.Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'warmer_games_screenshots' not in tables:
        op.create_table(
            'warmer_games_screenshots',
            sa.Column('uid', sa.Integer(), primary_key=True),
            sa.Column('result_id', sa.Integer, sa.ForeignKey('warmer_games_results.uid'), index=True),
            sa.Column('screenshot', Attachment(ScreenShotAttachedImage)),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )


def downgrade():
    op.drop_table('warmer_games_screenshots')
