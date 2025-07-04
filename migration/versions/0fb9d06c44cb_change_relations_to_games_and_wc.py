"""Change relations to game results and wednesday challenges from xuser to user

Revision ID: 0fb9d06c44cb
Revises: a01becafe8f7
Create Date: 2025-07-04 04:00:56.064049

"""

# revision identifiers, used by Alembic.
revision = '0fb9d06c44cb'
down_revision = 'a01becafe8f7'

from alembic import op
import sqlalchemy as sa

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

games_results_table = sa.Table(
    'games_results',
    sa.MetaData(),

    sa.Column('uid', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('tg_user.user_id'), index=True),
    sa.Column('xtwitter_uid', sa.Integer, sa.ForeignKey('xtwitter.uid'), index=True),
    sa.Column('game_no', sa.Integer, nullable=False, index=True, default=0),
    sa.Column('game_time', sa.Time, nullable=True, index=True),
    sa.Column('game_rows', sa.Integer, nullable=True, index=True),
    sa.Column('wednesday_challenge', sa.Boolean, nullable=True, index=True),
    sa.Column('comment', sa.UnicodeText, nullable=True),
    sa.Column('game_result_time', sa.Time, nullable=True, index=True),
    sa.Column('game_points', sa.Integer, nullable=False, index=True, default=0),
    sa.Column('game_rank', sa.Integer, nullable=True, index=True),
    sa.Column('game_raw_data', sa.UnicodeText(255), nullable=False, default=''),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now())
)

wednesday_challenge_words_table = sa.Table(
    'wednesday_challenge_words',
    sa.MetaData(),

    sa.Column('uid', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('tg_user.user_id'), index=True),
    sa.Column('xtwitter_uid', sa.Integer, sa.ForeignKey('xtwitter.uid'), index=True),
    sa.Column('game_no', sa.Integer, nullable=False, index=True, default=0),
    sa.Column('first_word', sa.Unicode(5), nullable=False, index=True, default=''),
    sa.Column('second_word', sa.Unicode(5), nullable=False, index=True, default=''),
    sa.Column('third_word', sa.Unicode(5), nullable=False, index=True, default=''),
    sa.Column('comment', sa.UnicodeText, nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column('updated', sa.DateTime(timezone=True), onupdate=sa.func.now())
)


def upgrade():
    connection = op.get_bind()

    op.add_column('games_results', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_games_results_user_id'), 'games_results', ['user_id'], unique=False)
    op.create_foreign_key(None, 'games_results', 'tg_user', ['user_id'], ['user_id'])

    op.add_column('wednesday_challenge_words', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_wednesday_challenge_words_user_id'), 'wednesday_challenge_words', ['user_id'], unique=False)
    op.create_foreign_key(None, 'wednesday_challenge_words', 'tg_user', ['user_id'], ['user_id'])

    for xuser in connection.execute(xtwitter_table.select()):
        connection.execute(games_results_table.update().values(user_id=xuser.user_id).where(games_results_table.c.xtwitter_uid == xuser.uid))
        connection.execute(wednesday_challenge_words_table.update().values(user_id=xuser.user_id).where(wednesday_challenge_words_table.c.xtwitter_uid == xuser.uid))

    op.drop_constraint('games_results_ibfk_1', 'games_results', 'foreignkey')
    op.drop_column('games_results', 'xtwitter_uid')

    op.drop_constraint('wednesday_challenge_words_ibfk_1', 'wednesday_challenge_words', 'foreignkey')
    op.drop_column('wednesday_challenge_words', 'xtwitter_uid')


def downgrade():
    connection = op.get_bind()

    op.add_column('wednesday_challenge_words', sa.Column('xtwitter_uid', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_wednesday_challenge_words_xtwitter_uid'), 'wednesday_challenge_words', ['xtwitter_uid'], unique=False)
    op.create_foreign_key('wednesday_challenge_words_ibfk_1', 'wednesday_challenge_words', 'xtwitter', ['xtwitter_uid'], ['uid'])

    op.add_column('games_results', sa.Column('xtwitter_uid', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_games_results_xtwitter_uid'), 'games_results', ['xtwitter_uid'], unique=False)
    op.create_foreign_key('games_results_ibfk_1', 'games_results', 'xtwitter', ['xtwitter_uid'], ['uid'])

    for xuser in connection.execute(xtwitter_table.select()):
        connection.execute(wednesday_challenge_words_table.update().values(xtwitter_uid=xuser.uid).where(wednesday_challenge_words_table.c.user_id == xuser.user_id))
        connection.execute(games_results_table.update().values(xtwitter_uid=xuser.uid).where(games_results_table.c.user_id == xuser.user_id))

    op.drop_constraint('wednesday_challenge_words_ibfk_2', 'wednesday_challenge_words', 'foreignkey')
    op.drop_column('wednesday_challenge_words', 'user_id')

    op.drop_constraint('games_results_ibfk_2', 'games_results', 'foreignkey')
    op.drop_column('games_results', 'user_id')
