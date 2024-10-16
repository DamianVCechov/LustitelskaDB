# -*- coding: utf-8 -*-
'''
Utilities.

Created on 16. 10. 2024

@author: jarda
'''

from lustitelskadb import model
from lustitelskadb.model import DBSession

__all__ = ('assemble_game_scoresheet')


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
            if row.game_rows == 1:
                row.game_rank = 0
            else:
                row.game_rank = next_place
                recentplace_counter += 1
        else:
            if next_place > 0:
                next_place = -1
                recentplace_counter = 0
            if not (prev_row and prev_row.game_time == row.game_time and prev_row.game_rows == row.game_rows and prev_row.game_result_time == row.game_result_time):
                next_place -= recentplace_counter
                recentplace_counter = 0
            row.game_rank = next_place
            recentplace_counter += 1

        prev_row = row

    if dbflush:
        DBSession.flush()

    return 0
