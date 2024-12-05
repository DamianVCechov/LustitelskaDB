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

__all__ = ['ResultForm', 'LibriCipherForm', 'XTwitterPostForm', 'LegacyDataImportForm']


class ResultForm(twf.Form):

    class child(twf.ListLayout):

        css_class = 'list-unstyled bg-light p-3 rounded'

        xtwitter_uid = twf.HiddenField()
        xtwitter_username = twf.HiddenField()
        xtwitter_displayname = twf.HiddenField()

        game_result = twf.TextArea(
            label=l_(u'Game result'),
            help_text=l_(u'Please Enter your game result (required)'),
            placeholder=l_(u'Game result'),
            validator=validators.ByteString(min=30),
            required=True,
            rows=12,
            attrs={
                'autofocus': True
            },
            css_class="form-control font-monospace fs-4 my-3"
        )

        wednesday_challenge = twf.CheckBox(
            label=l_(u'Wednesday challenge'),
            help_text=l_(u'Please check it if you play wednesday challenge'),
            validator=validators.Bool(),
            css_class="form-check-input d-block",
            required=False,
            attrs={
                'data-toggle': "toggle",
                'tristate': "tristate",
                'data-onlabel': l_("I played"),
                'data-offlabel': l_("I didn't played"),
                'data-onstyle': "success",
                'data-offstyle': "danger",
                'data-style': "my-3 me-3"
            }
        )

        comment = twf.TextArea(
            label=l_(u'Comments'),
            help_text=l_(u'Please Enter any comments (optional)'),
            placeholder=l_(u'Comments'),
            validator=validators.ByteString(),
            required=False,
            rows=5,
            css_class="form-control fs-4 my-3 noto-color-emoji-regular"
        )

        emoji_picker = twf.LinkField(
            label=html.literal('<div class="emoji-picker-tooltip" role="tooltip"><emoji-picker></emoji-picker></div>'),
            text=html.literal('<i class="bi bi-emoji-smile"></i>'),
            css_class="btn btn-outline-secondary",
            link="#"
        )

    action = lurl('/save_result')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-light btn-lg'
    )


class LibriCipherForm(twf.Form):

    class child(twf.ListLayout):

        css_class = 'list-unstyled bg-light p-3'

        uid = twf.HiddenField()

        part = twf.NumberField(
            label=l_(u'Part'),
            help_text=l_(u'Please Enter part number (required)'),
            placeholder=l_(u'Part'),
            validator=validators.Int(min=1),
            autofocus=True,
            required=True,
            css_class="form-control my-1"
        )

        question = twf.TextField(
            label=l_(u'Question'),
            help_text=l_(u'Please Enter Question (required)'),
            placeholder=l_(u'Question'),
            validator=validators.ByteString(max=100),
            required=True,
            css_class="form-control my-1"
        )

        description = twf.TextArea(
            label=l_(u'Description'),
            help_text=l_(u'Please Enter description (required)'),
            placeholder=l_(u'Description'),
            validator=validators.ByteString(),
            required=True,
            rows=5,
            css_class="form-control my-1 tinymce-override"
        )

        answer = twf.TextArea(
            label=l_(u'Answer'),
            help_text=l_(u'Please Enter Answer (required)'),
            placeholder=l_(u'Answer'),
            validator=validators.ByteString(),
            required=True,
            rows=5,
            css_class="form-control my-1 tinymce-override"
        )

    action = lurl('/admin/libricipher/save')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-outline-secondary btn-lg'
    )


class XTwitterPostForm(twd.CustomisedForm):

    class child(twf.ListLayout):

        css_class = 'list-unstyled bg-light p-3'

        text = twf.TextArea(
            label=l_(u'Post text'),
            help_text=l_(u'Please Enter X/Twitter post text'),
            placeholder=l_(u'Post text'),
            validator=validators.ByteString(max=280),
            maxlength=280,
            required=True,
            rows=5,
            css_class="form-control my-1",
            attrs={
                'autofocus': True
            }
        )

        class MediaList(twd.GrowingGridLayout):
            """Media list for post."""

            label = l_(u"Media list")

            media = twf.FileField(
                label='',
                validator=validators.FieldStorageUploadConverter(),
                css_class="form-control form-control-sm"
            )

    action = lurl('/admin/xtwitter/create_post')

    submit = twf.SubmitButton(
        value=l_(u'Submit'),
        css_class='btn btn-outline-secondary btn-lg'
    )


class LegacyDataImportForm(twf.Form):

    class child(twf.ListLayout):

        css_class = 'list-unstyled bg-light p-3'

        csv_file = twf.FileField(
            label=l_('CSV file with legacy data'),
            help_text=l_(u'Please browse CSV file with legacy data to import it into database'),
            validator=validators.FieldStorageUploadConverter(),
            css_class="form-control form-control-lg mt-3"
        )

    action = lurl('/admin/process_legacy_import')

    submit = twf.SubmitButton(
        value=l_(u'Import'),
        css_class='btn btn-outline-secondary btn-lg'
    )
