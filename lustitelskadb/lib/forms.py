# -*- encoding: utf-8 -*-
'''
App Forms

Created on 23. 8. 2024

@author: jarda
'''

import logging
log = logging.getLogger(__name__)

from tg import url, lurl
from tg.i18n import ugettext as _, lazy_ugettext as l_

import tw2.core as twc
import tw2.forms as twf
import tw2.dynforms as twd

from formencode import validators

# Python 2.7 compatibility hack
try:
    ModuleNotFoundError
except NameError:
    ModuleNotFoundError = ImportError

try:
    from webhelpers2 import html
except (ImportError, ModuleNotFoundError, SyntaxError):
    try:
        from webhelpers import html
    except:
        log.error("WebHelpers(2) helpers not available with this Python Version")

__all__ = ['ResultForm']


class ResultForm(twf.Form):

    class child(twf.ListLayout):

        css_class = 'list-unstyled bg-light p-3'

        nickname = twf.TextField(
            label=l_(u'Nickname'),
            help_text=l_(u'Please Enter your nickname (required)'),
            placeholder=l_(u'Your nickname'),
            validator=validators.ByteString(min=2,max=64),
            minlenght=2,
            maxlength=64,
            autofocus=True,
            required=True,
            css_class="form-control my-3"
        )

        game_result = twf.TextArea(
            label=l_(u'Game result'),
            help_text=l_(u'Please Enter your game result (required)'),
            placeholder=l_(u'Game result'),
            validator=validators.ByteString(min=30),
            minlength=30,
            required=True,
            rows=12,
            css_class="form-control font-monospace fs-4 my-3"
        )

        wednesday_challenge = twf.CheckBox(
            label=l_(u'Wednesday challenge'),
            help_text=l_(u'Please check it if you play wednesday challenge'),
            validator=validators.Bool(),
            css_class="form-check-input my-3 p-3 d-block"
        )

        comment = twf.TextArea(
            label=l_(u'Comments'),
            help_text=l_(u'Please Enter any comments (optional)'),
            placeholder=l_(u'Comments'),
            validator=validators.ByteString(),
            required=False,
            rows=5,
            css_class="form-control my-3"
        )

    action = lurl('/save_result')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-outline-secondary btn-lg'
    )
