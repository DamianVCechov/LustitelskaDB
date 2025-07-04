"""Create local accounts if does not exists

Revision ID: a01becafe8f7
Revises: e09a86ac2731
Create Date: 2025-07-04 01:22:51.039156

"""

# revision identifiers, used by Alembic.
revision = 'a01becafe8f7'
down_revision = 'e09a86ac2731'

from alembic import op
import sqlalchemy as sa

from datetime import datetime

xtwitter_table = sa.Table(
    'xtwitter',
    sa.MetaData(),

    sa.Column('uid', sa.Integer, primary_key=True),
    sa.Column('xid', sa.String(20), unique=True, nullable=False, default=''),
    sa.Column('user_name', sa.Unicode(15), unique=True, nullable=False, default=u''),
    sa.Column('display_name', sa.Unicode(50), unique=False, nullable=False, default=u''),
    sa.Column('user_info', sa.UnicodeText),

    sa.Column('user_id', sa.Integer, sa.ForeignKey('tg_user.user_id'), index=True)
)

user_table = sa.Table(
    'tg_user',
    sa.MetaData(),

    sa.Column('user_id', sa.Integer, autoincrement=True, primary_key=True),
    sa.Column('user_name', sa.Unicode(16), unique=True, nullable=False),
    sa.Column('email_address', sa.Unicode(255), unique=True, nullable=False),
    sa.Column('display_name', sa.Unicode(255)),
    sa.Column('password', sa.Unicode(128)),
    sa.Column('created', sa.DateTime, default=datetime.now)
)


def upgrade():
    connection = op.get_bind()

    for xuser in connection.execute(xtwitter_table.select().where(xtwitter_table.c.user_id == None)):
        result = connection.execute(user_table.insert().values(
            user_name=xuser.user_name,
            email_address='{}@notdomain.none'.format(xuser.user_name),
            display_name=xuser.display_name
        ))
        connection.execute(xtwitter_table.update().values(user_id=result.inserted_primary_key[0]).where(xtwitter_table.c.uid == xuser.uid))


def downgrade():
    pass
