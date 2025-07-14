# -*- coding: utf-8 -*-
'''
Utilities.

Created on 16. 10. 2024

@author: jarda
'''

from lustitelskadb import model
from lustitelskadb.model import DBSession

from datetime import datetime, timedelta

__all__ = ('assemble_game_scoresheet', 'today_game_no', 'user_rank_hours_offset')

scoring = {
    0: 0,
    1: 6,
    2: 5,
    3: 4,
    4: 3,
    5: 2
}

user_rank_hours_offset = {
    1: 0,
    2: 5,
    3: 10,
    4: 15,
    5: 20
}

HADEJSLOVA_STARTDATE = datetime(2022, 1, 14, 18)


def assemble_game_scoresheet(game_no, dbflush=True):
    """Assemble Game Scoresheet"""
    game = DBSession.query(model.GameResult).filter(model.GameResult.game_no == game_no)
    if game_no % 7 == 5:
        game = game.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.wednesday_challenge.desc(), model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())
    else:
        game = game.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())

    next_place = 1
    recentplace_counter = 0
    prev_row = None

    for row in game.all():
        if row.game_rows:
            if not (prev_row and prev_row.game_time == row.game_time and prev_row.game_rows == row.game_rows and prev_row.game_result_time == row.game_result_time):
                next_place += recentplace_counter
                recentplace_counter = 0
            if game_no % 7 == 5 and prev_row and prev_row.wednesday_challenge and not row.wednesday_challenge:
                next_place = 1
                recentplace_counter = 0
                if prev_row.game_rank > 5:
                    prev_row.game_points = 0
            if row.game_rows == 1:
                row.game_rank = 0
                row.game_game_points = 0
            else:
                row.game_rank = next_place
                row.game_points = scoring.get(next_place, 1)
                recentplace_counter += 1
        else:
            if prev_row and prev_row.game_rows and prev_row.game_rank > 5:
                prev_row.game_points = 0
            if next_place > 0:
                next_place = -1
                recentplace_counter = 0
            if game_no % 7 == 5 and prev_row and prev_row.wednesday_challenge and not row.wednesday_challenge:
                next_place = -1
                recentplace_counter = 0
            if not (prev_row and prev_row.game_time == row.game_time and prev_row.game_rows == row.game_rows and prev_row.game_result_time == row.game_result_time):
                next_place -= recentplace_counter
                recentplace_counter = 0
            row.game_rank = next_place
            row.game_points = 0
            recentplace_counter += 1

        prev_row = row

    if row.game_rows and row.game_rank > 5:
        row.game_points = 0

    if dbflush:
        DBSession.flush()

    return 0


def today_game_no():
    """Count today's game no."""
    now = datetime.now()
    td = timedelta(1)
    if now.hour < 18:
        game_begin = datetime((now - td).year, (now - td).month, (now - td).day, 18)
        game_finish = datetime(now.year, now.month, now.day, 17, 59, 59, 999999)
    else:
        game_begin = datetime(now.year, now.month, now.day, 18)
        game_finish = datetime((now + td).year, (now + td).month, (now + td).day, 17, 59, 59, 999999)

    return (game_finish - HADEJSLOVA_STARTDATE).days
