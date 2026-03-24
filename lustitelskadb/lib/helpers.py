# -*- coding: utf-8 -*-
"""Template Helpers used in LustitelskaDB."""
import logging
from markupsafe import Markup
from datetime import datetime, date, timedelta
from lustitelskadb.lib.utils import HADEJSLOVA_STARTDATE

log = logging.getLogger(__name__)

FIRST_SPECIAL_DATES = {
    '01.01': '&#x1F386;',  # Fireworks
    '14.03': '&Pi;',  # Pi Day
    '01.04': '&#x1F0CF;',  # Playing Card Black Joker - Fool's day
    '01.11': '&#x1F47B;',  # Ghost - All Saints Day & Día de los Muertos
    '02.11': '&#x1F47B;',  # Ghost - Día de los Muertos
    '24.12': '&#x1F384;',  # Christmas Tree
    '25.12': '&#x1F384;',  # Christmas Tree
    '26.12': '&#x1F384;',  # Christmas Tree
    '31.12': '&#x1F386;'  # Fireworks
}

SECOND_SPECIAL_DATES = {
    '14.03': '&pi;'  # pi Day
}

FOURTH_SPECIAL_DATES = {
    '08.03': '&#x1F339;',  # Rose - International Women's Day
    '14.03': '&#x1F967;',  # Pie - Pi Day
    '15.03': '&#x1F634;',  # Sleeping Face - World Sleep Day
    '31.07': '&#x1F346;',  # Aubergine - National Orgasm Day
    '08.08': '&#x1F346;'  # Aubergine - International Female Orgasm Day
}

FIFTH_SPECIAL_DATES = {
    '14.03': '&#x1F427;',  # Penguin - Czech name-day Rút
    '15.03': '&#x1F6CC;',  # Sleeping Accommodation - World Sleep Day
    '26.03': '&#x1F410;',  # Goat - Free The Nipple Day
    '01.04': '&#x1F40C;',  # Snail
    '17.09': '&#x1F427;',  # Penguin - 1st release of Linux
    '13.10': '&#x1F410;',  # Goat - National Bra Day
    '24.12': '&#x26C4;',  # Snowman Without Snow
    '25.12': '&#x26C4;',  # Snowman Without Snow
    '26.12': '&#x26C4;'  # Snowman Without Snow
}

LAST_SPECIAL_DATES = {
    '01.01': '&#x1F387;',  # Firework Sparkler
    '15.02': '&#x1F4BB;',  # Personal Computer - World Computer Day
    '12.03': '&#x1F526;',  # Electric torch - Invented in 12.3.1898
    '15.03': '&#x1F4A4;',  # Sleeping Symbol - World Sleep Day
    '17.03': '&#x1F382;',  # Birthday cake - This DB B-day
    '15.09': '&#x1F365;',  # Fish Cake with Swirl Design - 1st releaseof Debian
    '21.10': '&#x1F4A1;',  # Bulb - Invented in 21.10.1879
    '29.10': '&#x1FA94;',  # Aladdin's lamp - name-day of Aladdin
    '31.10': '&#x1F383;',  # Jack-O-Lantern - Halloween
    '01.11': '&#x1F56F;',  # Candle - All Saints Day & Día de los Muertos
    '24.12': '&#x2744;',  # Snowflake
    '25.12': '&#x2744;',  # Snowflake
    '26.12': '&#x2744;',  # Snowflake
    '31.12': '&#x1F387;'  # Firework Sparkler
}


def now():
    return datetime.now()


def today():
    return date.today()


def current_year():
    return now().strftime('%Y')


def icon(icon_name):
    return Markup('<i class="glyphicon glyphicon-%s"></i>' % icon_name)


def bicon(icon_name, fs=None, color=None):
    return Markup('<i class="bi bi-%s%s%s"></i>' % (icon_name, (' fs-%i' % fs) if fs else '', (' text-%s' % color) if color else ''))


def wednesday_challenge_words_window():
    now_dt = now()
    if now_dt.weekday() == 1 and now_dt.hour >= 18 or now_dt.weekday() == 2 and now_dt.hour < 18:
        return True
    else:
        return False


def wednesday_challenge_comming():
    now_dt = now()
    if now_dt.weekday() == 2 and now_dt.hour >= 18 or now_dt.weekday() == 3 and now_dt.hour < 18:
        return True
    else:
        return False


def game_no_start_date(game_no):
    """Count date from and to for game no."""
    return HADEJSLOVA_STARTDATE + timedelta(days=game_no)


def badge(rank, default=''):
    """Get badge for game rank."""
    return {
        -1: '&#x1FAA3;',
        -2: '&#x1FA9F;',
        -3: '&#x1F52E;',
        '-last': '&#x1F42E;',
        0: '&#x1F984;',
        1: FIRST_SPECIAL_DATES.get(now().strftime('%d.%m'), '&#x1F947;'),
        2: SECOND_SPECIAL_DATES.get(now().strftime('%d.%m'), '&#x1F948;'),
        3: '&#x1F949;',
        4: FOURTH_SPECIAL_DATES.get(now().strftime('%d.%m'), '&#x1F954;'),
        5: FIFTH_SPECIAL_DATES.get(now().strftime('%d.%m'), '&#x1F422;'),
        # 6: '&#x1FBF6;',
        # 7: '&#x1FBF7;',
        # 8: '&#x1FBF8;',
        # 9: '&#x1FBF9;',
        'leaf': '&#x1F343;',  # Leaf Fluttering In Wind
        'last': LAST_SPECIAL_DATES.get(now().strftime('%d.%m'), '&#x1F3EE;')
    }.get(rank, default)


# Import some operators for using in templates, because of problematic using > and < chars
from operator import lt, le, gt, ge

# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")
