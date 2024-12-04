# -*- coding: utf-8 -*-
"""API controller module"""

from tg import expose, redirect, validate, flash, url, config, abort, response
# from tg.i18n import ugettext as _
# from tg import predicates
from tg.support.converters import asbool

from lustitelskadb.lib.base import BaseController
from lustitelskadb import model
from lustitelskadb.model import DBSession

from datetime import datetime, timedelta
import csv

try:
    from StringIO import StringIO
except:
    from io import StringIO

from lustitelskadb.lib.utils import HADEJSLOVA_STARTDATE

try:
    unichr
except:
    unichr = chr

BADGE = {
    -1: unichr(0x1F4A9),  # Poop
    0: unichr(0x1F984),  # Unicorn
    1: unichr(0x1F947),  # Medal #1
    2: unichr(0x1F948),  # Medal #2
    3: unichr(0x1F949),  # Medal #3
    4: unichr(0x1F954),  # Potato
    5: unichr(0x1F422),  # Turtle
    # 6: unichr(0x1FBF6),
    # 7: unichr(0x1FBF7),
    # 8: unichr(0x1FBF8),
    # 9: unichr(0x1FBF9),
    'leaf': unichr(0x1F343),  # Leaf Fluttering In Wind
    'last': unichr(0x1F3EE)  # Lantern
}


def encode(obj, code):
    """
    Encode Python2 + Python 3 compatibility function.
    """
    try:
        unicode
        return obj.encode(code)
    except:
        return obj


class APIController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()

    @expose()
    def index(self, **kw):
        return redirect('/')

    @expose('json')
    def get_new_records(self, last_fetched_uid=None, **kw):
        """Get new records from last UID"""
        if not last_fetched_uid:
            return dict(data=[], status_code=-1, status_txt="Error", error=True, status_msg="No last UID on input.")

        records = DBSession.query(model.GameResult).filter(model.GameResult.uid > last_fetched_uid).all()
        if not records:
            return dict(data=[], status=0, status_txt="OK", error=False, status_msg="No new records found.")

        data = [{
            'uid': item.uid,
            'user_name': item.xtwitter.user_name,
            'display_name': item.xtwitter.display_name,
            'game': item.game_no,
            'time': item.game_time,
            'rows': item.game_rows,
            'wchallenge': item.wednesday_challenge,
            'wchallenge_s': config.get('api.wednesday_challenge.map.None', "") if item.wednesday_challenge == None else (config.get('api.wednesday_challenge.map.True', "✅") if item.wednesday_challenge else config.get('api.wednesday_challenge.map.False', "❎")),
            'comment': item.comment,
            'result': item.game_result_time,
            'points': item.game_points,
            'rank': item.game_rank,
            'raw_data': item.game_raw_data,
            'created': item.created,
            'updated': item.updated,
        } for item in records]

        return dict(data=data, status_code=0, status_txt="OK", error=False, status_msg="New records found.")

    @expose()
    def fetch_game_data(self, game=None, convert=False, **kw):
        """Export game data."""
        if game not in ('ongoing', 'final'):
            abort(status_code=422, detail="Missing game type to export")

        data_cols = (
            ('game_rank', 'game_rank'),
            ('user_name', 'xtwitter.user_name'),
            ('game_time', 'game_time'),
            ('game_rows', 'game_rows'),
            ('wednesday_challenge', 'wednesday_challenge'),
            ('game_result_time', 'game_result_time')
        )

        now = datetime.now()
        td = timedelta(1)
        if now.hour < 18:
            game_begin = datetime((now - td).year, (now - td).month, (now - td).day, 18)
            game_finish = datetime(now.year, now.month, now.day, 17, 59, 59, 999999)
        else:
            game_begin = datetime(now.year, now.month, now.day, 18)
            game_finish = datetime((now + td).year, (now + td).month, (now + td).day, 17, 59, 59, 999999)
        game_in_progress = (game_finish - HADEJSLOVA_STARTDATE).days
        game_no = game_in_progress
        if game == 'final':
            game_no -= 1

        game_data = DBSession.query(model.GameResult).filter(model.GameResult.game_no == game_no)
        if game_no % 7 == 5:
            game_data = game_data.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.wednesday_challenge.desc(), model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())
        else:
            game_data = game_data.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())

        csv_stream = StringIO()
        csv_writer = csv.DictWriter(csv_stream, fieldnames=[r[0] for r in data_cols], dialect="excel")
        csv_writer.writeheader()

        for row in game_data.all():
            csv_row = {}.fromkeys([r[0] for r in data_cols])
            for k, v in data_cols:
                if '.' in v:
                    c, m = v.split('.')
                    csv_row[k] = encode(getattr(getattr(row, c, {}), m, ''), 'utf-8')
                else:
                    csv_row[k] = encode(getattr(row, v, ''), 'utf-8')
            if asbool(convert):
                csv_row['game_rank'] = encode(BADGE.get(row.game_rank, row.game_rank), 'utf-8')
                if row.wednesday_challenge and game_no % 7 == 5:
                    csv_row['wednesday_challenge'] = encode(unichr(0x2705), 'utf-8')
                if row.game_rank < 0 and not row.game_result_time:
                    csv_row['game_result_time'] = 'PROHRA'
                elif row.game_rank > 0 and row.game_rows > 1 and not row.game_result_time:
                    csv_row['game_rank'] = encode(BADGE.get('leaf', row.game_rank), 'utf-8')
                elif row.game_rank > 0 and row.game_points == 0:
                    csv_row['game_rank'] = encode(BADGE.get('last', row.game_rank), 'utf-8')
            csv_writer.writerow(csv_row)

        # response.headerlist.append(('Content-Disposition', 'inline; filename=lustitelskadb_{}_game-{}.csv'.format(game, now)))
        response.headerlist.append(('Content-Disposition', 'attachment; filename=lustitelskadb_{}_game-{}.csv'.format(game, now)))

        return csv_stream.getvalue()
