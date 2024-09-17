# -*- coding: utf-8 -*-
"""Template Helpers used in LustitelskaDB."""
import logging
from markupsafe import Markup
from datetime import datetime

log = logging.getLogger(__name__)


def current_year():
    now = datetime.now()
    return now.strftime('%Y')


def icon(icon_name):
    return Markup('<i class="glyphicon glyphicon-%s"></i>' % icon_name)


def bicon(icon_name, fs=None, color=None):
    return Markup('<i class="bi bi-%s%s%s"></i>' % (icon_name, (' fs-%i' % fs) if fs else '', (' text-%s' % color) if color else ''))


# Import commonly used helpers from WebHelpers2 and TG
from tg.util.html import script_json_encode

try:
    from webhelpers2 import date, html, number, misc, text
except SyntaxError:
    log.error("WebHelpers2 helpers not available with this Python Version")
