# -*- coding: utf-8 -*-
"""Template Helpers used in LustitelskaDB."""
import logging
from markupsafe import Markup
from datetime import datetime, date

log = logging.getLogger(__name__)


def now():
    return datetime.now()


def today():
    return date.today()


def current_year():
    now = datetime.now()
    return now.strftime('%Y')


def icon(icon_name):
    return Markup('<i class="glyphicon glyphicon-%s"></i>' % icon_name)


def bicon(icon_name, fs=None, color=None):
    return Markup('<i class="bi bi-%s%s%s"></i>' % (icon_name, (' fs-%i' % fs) if fs else '', (' text-%s' % color) if color else ''))


def wednesday_challenge_words_window():
    now = datetime.now()
    if now.weekday() == 1 and now.hour >= 18 or now.weekday() == 2 and now.hour < 18:
        return True
    else:
        return False

def wednesday_challenge_comming():
    now = datetime.now()
    if now.weekday() == 2 and now.hour >= 18 or now.weekday() == 3 and now.hour < 18:
        return True
    else:
        return False


# Import some operators for using in templates, because of problematic using > and < chars
from operator import lt, le, gt, ge

# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")
