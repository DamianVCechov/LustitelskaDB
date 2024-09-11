# -*- coding: utf-8 -*-
"""API controller module"""

from tg import expose, redirect, validate, flash, url
# from tg.i18n import ugettext as _
# from tg import predicates

from lustitelskadb.lib.base import BaseController
from lustitelskadb import model
from lustitelskadb.model import DBSession


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
            'comment': item.comment,
            'result': item.game_result_time,
            'points': item.game_points,
            'rank': item.game_rank,
            'raw_data': item.game_raw_data,
            'created': item.created,
            'updated': item.updated,
        } for item in records]

        return dict(data=data, status_code=0, status_txt="OK", error=False, status_msg="New records found.")
