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

import magic

import tw2.core as twc
import tw2.forms as twf
import tw2.dynforms as twd

from registration.lib.validators import UniqueEmailValidator, UniqueUserValidator
from resetpassword.lib.validators import RegisteredUserValidator
from formencode import validators
from formencode.compound import Pipe as FEPipe
from formencode.api import FancyValidator, Invalid as FEInvalid, NoDefault as FENoDefault
from formencode.foreach import ForEach as FEForEach

from lustitelskadb.lib.injects import (
    filepond_image_preview_css, filepond_image_preview_js, filepond_file_validate_type_js, filepond_css, filepond_js,
    filepond_init
)

# Python 2.7 compatibility hack
try:
    ModuleNotFoundError
except NameError:
    ModuleNotFoundError = ImportError

# Another Python 2.7 compatibility hack
try:
    unicode
except (NameError):
    unicode = str

try:
    from webhelpers2 import html
except (ImportError, ModuleNotFoundError, SyntaxError):
    try:
        from webhelpers import html
    except:
        log.error("WebHelpers(2) helpers not available with this Python Version")

__all__ = (
    'ResultForm', 'ResultAdminForm', 'WarmerResultForm', 'WarmerResultAdminForm', 'WednesdayChallengeWordsForm',
    'LibriCipherForm', 'XTwitterPostForm', 'LegacyDataImportForm',
    'UserRegistration', 'NewPasswordForm', 'ResetPasswordForm', 'UserProfileEditForm', 'UserProfileChangePasswordForm'
)


def MultipleFileUpload(
        required=False,
        file_validator=None,
        max_files=None,
        max_files_error=u'You can upload a maximum of %(maxLength)i files'
):
    upload_validator = validators.FieldStorageUploadConverter(
        not_empty=True
    )

    if file_validator is not None:
        upload_validator = FEPipe(
            upload_validator,
            file_validator
        )

    kwargs = {
        'convert_to_list': True,
    }

    if required:
        kwargs.update({
            'not_empty': True,
            'if_missing': FENoDefault,
        })

    validator = FEForEach(
        upload_validator,
        **kwargs
    )

    if max_files is not None:
        validator = FEPipe(
            validator,
            validators.MaxLength(
                max_files,
                messages={
                    'tooLong': max_files_error
                }
            )
        )

    return validator


class MimeTypeValidator(FancyValidator):
    allowed_types = (
        'image/*',
    )
    error_message = 'Invalid file type'

    def _validate_python(self, value, state):
        position = value.file.tell()

        try:
            value.file.seek(0)
            data = value.file.read(2048)

            mime_type = magic.from_buffer(data, mime=True)

        finally:
            value.file.seek(position)

        for allowed_type in self.allowed_types:
            if allowed_type.endswith('/*'):
                prefix = allowed_type[:-1]

                if mime_type.startswith(prefix):
                    return

            elif mime_type == allowed_type:
                return

        raise FEInvalid(
            unicode(self.error_message),
            value,
            state
        )


class FilePondField(twf.FileField):
    max_files = twc.Param(
        'Maximum number of files',
        default=None
    )

    label_idle = twc.Param(
        'FilePond idle label',
        default='Drag & Drop your files or {browse}'
    )

    label_browse = twc.Param(
        'FilePond browse label',
        default='Browse'
    )

    label_invalid_field = twc.Param(
        'Invalid field label',
        default='Field contains invalid files'
    )

    label_file_waiting_for_size = twc.Param(
        'Waiting for file size label',
        default='Waiting for size'
    )

    label_file_size_not_available = twc.Param(
        'File size unavailable label',
        default='Size not available'
    )

    label_file_loading = twc.Param(
        'File loading label',
        default='Loading'
    )

    label_file_load_error = twc.Param(
        'File load error label',
        default='Error during load'
    )

    label_file_processing = twc.Param(
        'File processing label',
        default='Uploading'
    )

    label_file_processing_complete = twc.Param(
        'File processing complete label',
        default='Upload complete'
    )

    label_file_processing_aborted = twc.Param(
        'File processing aborted label',
        default='Upload cancelled'
    )

    label_file_processing_error = twc.Param(
        'File processing error label',
        default='Error during upload'
    )

    label_file_processing_revert_error = twc.Param(
        'File processing revert error label',
        default='Error during revert'
    )

    label_file_remove_error = twc.Param(
        'File remove error label',
        default='Error during remove'
    )

    label_tap_to_cancel = twc.Param(
        'Tap to cancel label',
        default='tap to cancel'
    )

    label_tap_to_retry = twc.Param(
        'Tap to retry label',
        default='tap to retry'
    )

    label_tap_to_undo = twc.Param(
        'Tap to undo label',
        default='tap to undo'
    )

    label_button_remove_item = twc.Param(
        'Remove item button label',
        default='Remove'
    )

    label_button_abort_item_load = twc.Param(
        'Abort item load button label',
        default='Abort'
    )

    label_button_retry_item_load = twc.Param(
        'Retry item load button label',
        default='Retry'
    )

    label_button_abort_item_processing = twc.Param(
        'Abort item processing button label',
        default='Cancel'
    )

    label_button_undo_item_processing = twc.Param(
        'Undo item processing button label',
        default='Undo'
    )

    label_button_retry_item_processing = twc.Param(
        'Retry item processing button label',
        default='Retry'
    )

    label_button_process_item = twc.Param(
        'Process item button label',
        default='Upload'
    )

    label_file_type_not_allowed = twc.Param(
        'Invalid file type label',
        default='File of invalid type'
    )

    file_validate_type_label_expected_types = twc.Param(
        'Expected file types label',
        default='Expects {allButLastType} or {lastType}'
    )

    resources = [
        filepond_css,
        filepond_image_preview_css,

        filepond_js,
        filepond_image_preview_js,
        filepond_file_validate_type_js,

        filepond_init
    ]

    def prepare(self):
        attrs = dict(self.attrs or {})
        attrs['data-filepond'] = 'true'

        if self.max_files is not None:
            attrs['data-max-files'] = unicode(self.max_files)

        label_idle = unicode(self.label_idle).format(
            browse='<span class="filepond--label-action">{}</span>'.format(self.label_browse)
        )

        attrs.update({
            'data-filepond-label-idle':
                label_idle,

            'data-filepond-label-invalid-field':
                unicode(self.label_invalid_field),

            'data-filepond-label-file-waiting-for-size':
                unicode(self.label_file_waiting_for_size),

            'data-filepond-label-file-size-not-available':
                unicode(self.label_file_size_not_available),

            'data-filepond-label-file-loading':
                unicode(self.label_file_loading),

            'data-filepond-label-file-load-error':
                unicode(self.label_file_load_error),

            'data-filepond-label-file-processing':
                unicode(self.label_file_processing),

            'data-filepond-label-file-processing-complete':
                unicode(self.label_file_processing_complete),

            'data-filepond-label-file-processing-aborted':
                unicode(self.label_file_processing_aborted),

            'data-filepond-label-file-processing-error':
                unicode(self.label_file_processing_error),

            'data-filepond-label-file-processing-revert-error':
                unicode(self.label_file_processing_revert_error),

            'data-filepond-label-file-remove-error':
                unicode(self.label_file_remove_error),

            'data-filepond-label-tap-to-cancel':
                unicode(self.label_tap_to_cancel),

            'data-filepond-label-tap-to-retry':
                unicode(self.label_tap_to_retry),

            'data-filepond-label-tap-to-undo':
                unicode(self.label_tap_to_undo),

            'data-filepond-label-button-remove-item':
                unicode(self.label_button_remove_item),

            'data-filepond-label-button-abort-item-load':
                unicode(self.label_button_abort_item_load),

            'data-filepond-label-button-retry-item-load':
                unicode(self.label_button_retry_item_load),

            'data-filepond-label-button-abort-item-processing':
                unicode(self.label_button_abort_item_processing),

            'data-filepond-label-button-undo-item-processing':
                unicode(self.label_button_undo_item_processing),

            'data-filepond-label-button-retry-item-processing':
                unicode(self.label_button_retry_item_processing),

            'data-filepond-label-button-process-item':
                unicode(self.label_button_process_item),

            'data-filepond-label-file-type-not-allowed':
                unicode(self.label_file_type_not_allowed),

            'data-filepond-file-validate-type-label-expected-types':
                unicode(self.file_validate_type_label_expected_types)
        })

        self.attrs = attrs

        super(FilePondField, self).prepare()


class ResultForm(twf.Form):
    class child(twf.ListLayout):
        css_class = 'list-unstyled bg-light p-3 rounded'

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
            css_class="form-check-input d-block p-3 my-3",
            required=False,
            attrs={
                'onchange': '$(this).prop("required", false);'
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


class ResultAdminForm(twf.Form):
    class child(ResultForm.child):

        user_id = twf.SingleSelectField(
            label=l_("User"),
            help_text=l_("Please select the user whose result you want to save."),
            placeholder=l_("User"),
            options=[],
            validator=validators.Int(not_empty=True),
            required=True,
            css_class="form-select noto-color-emoji-regular"
        )

        @classmethod
        def post_define(cls):
            if not getattr(cls, 'children', None):
                return

            for i, w in enumerate(cls.children):
                if getattr(w, 'id', None) == 'user_id':
                    cls.children.insert(0, cls.children.pop(i))
                    break

    action = lurl('/admin/save_result')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-light btn-lg'
    )


class WarmerResultForm(twf.Form):
    class child(twf.ListLayout):
        css_class = 'list-unstyled bg-light p-3 rounded'

        game_guesses = twf.NumberField(
            label=l_(u'Game guesses'),
            help_text=l_(u'Please Enter your game guesses (required)'),
            placeholder=l_(u'Game guesses'),
            validator=validators.Int(min=1),
            min=1,
            max=32767,
            required=True,
            autofocus=True,
            css_class="form-control font-monospace fs-4 my-3"
        )

        game_screenshots = FilePondField(
            label=l_(u'Game Screenshots'),
            help_text=l_(u'Upload game screenshots (mandatory)'),

            label_idle=l_(u'Drag & Drop your files or {browse}'),
            label_browse=l_(u'Browse'),

            label_invalid_field=l_(u'Field contains invalid files'),

            label_file_waiting_for_size=l_(u'Waiting for size'),
            label_file_size_not_available=l_(u'Size not available'),
            label_file_loading=l_(u'Loading'),
            label_file_load_error=l_(u'Error during load'),

            label_file_processing=l_(u'Uploading'),
            label_file_processing_complete=l_(u'Upload complete'),
            label_file_processing_aborted=l_(u'Upload cancelled'),
            label_file_processing_error=l_(u'Error during upload'),
            label_file_processing_revert_error=l_(u'Error during revert'),
            label_file_remove_error=l_(u'Error during remove'),

            label_tap_to_cancel=l_(u'tap to cancel'),
            label_tap_to_retry=l_(u'tap to retry'),
            label_tap_to_undo=l_(u'tap to undo'),

            label_button_remove_item=l_(u'Remove'),
            label_button_abort_item_load=l_(u'Abort'),
            label_button_retry_item_load=l_(u'Retry'),
            label_button_abort_item_processing=l_(u'Cancel'),
            label_button_undo_item_processing=l_(u'Undo'),
            label_button_retry_item_processing=l_(u'Retry'),
            label_button_process_item=l_(u'Upload'),

            label_file_type_not_allowed=l_(u'File of invalid type'),
            file_validate_type_label_expected_types=l_(u'Only image files are allowed'),

            validator=MultipleFileUpload(
                required=True,
                max_files=10,
                max_files_error=l_(u'You can upload a maximum of %(maxLength)i files'),
                file_validator=MimeTypeValidator(
                    allowed_types=('image/*',),
                    error_message=l_(u'Only image files are allowed')
                )
            ),
            required=True,
            attrs={
                'multiple': True,
                'accept': 'image/*'
            },
            css_class="form-control fs-4 my-3"
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

    action = lurl('/save_warmer_result')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-light btn-lg'
    )


class WarmerResultAdminForm(twf.Form):
    class child(twf.ListLayout):
        css_class = 'list-unstyled bg-light p-3 rounded'

        user_id = twf.SingleSelectField(
            label=l_("User"),
            help_text=l_("Please select the user whose result you want to save."),
            placeholder=l_("User"),
            options=[],
            validator=validators.Int(not_empty=True),
            required=True,
            css_class="form-select noto-color-emoji-regular"
        )

        game_guesses = twf.NumberField(
            label=l_(u'Game guesses'),
            help_text=l_(u'Please Enter your game guesses (required)'),
            placeholder=l_(u'Game guesses'),
            validator=validators.Int(min=1),
            min=1,
            max=32767,
            required=True,
            autofocus=True,
            css_class="form-control font-monospace fs-4 my-3"
        )

        game_screenshots = FilePondField(
            label=l_(u'Game Screenshots'),
            help_text=l_(u'Upload game screenshots (mandatory)'),

            label_idle=l_(u'Drag & Drop your files or {browse}'),
            label_browse=l_(u'Browse'),

            label_invalid_field=l_(u'Field contains invalid files'),

            label_file_waiting_for_size=l_(u'Waiting for size'),
            label_file_size_not_available=l_(u'Size not available'),
            label_file_loading=l_(u'Loading'),
            label_file_load_error=l_(u'Error during load'),

            label_file_processing=l_(u'Uploading'),
            label_file_processing_complete=l_(u'Upload complete'),
            label_file_processing_aborted=l_(u'Upload cancelled'),
            label_file_processing_error=l_(u'Error during upload'),
            label_file_processing_revert_error=l_(u'Error during revert'),
            label_file_remove_error=l_(u'Error during remove'),

            label_tap_to_cancel=l_(u'tap to cancel'),
            label_tap_to_retry=l_(u'tap to retry'),
            label_tap_to_undo=l_(u'tap to undo'),

            label_button_remove_item=l_(u'Remove'),
            label_button_abort_item_load=l_(u'Abort'),
            label_button_retry_item_load=l_(u'Retry'),
            label_button_abort_item_processing=l_(u'Cancel'),
            label_button_undo_item_processing=l_(u'Undo'),
            label_button_retry_item_processing=l_(u'Retry'),
            label_button_process_item=l_(u'Upload'),

            label_file_type_not_allowed=l_(u'File of invalid type'),
            file_validate_type_label_expected_types=l_(u'Only image files are allowed'),

            validator=MultipleFileUpload(
                max_files=10,
                max_files_error=l_(u'You can upload a maximum of %(maxLength)i files'),
                file_validator=MimeTypeValidator(
                    allowed_types=('image/*',),
                    error_message=l_(u'Only image files are allowed')
                )
            ),
            attrs={
                'multiple': True,
                'accept': 'image/*'
            },
            css_class="form-control fs-4 my-3"
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

    action = lurl('/admin/save_warmer_result')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-light btn-lg'
    )


class WednesdayChallengeWordsForm(twf.Form):
    class child(twf.ListLayout):
        css_class = 'list-unstyled bg-light p-3 rounded'

        first_word = twf.TextField(
            label=l_(u'First word'),
            help_text=l_(u'Please Enter Wednesday challenge first word (required)'),
            placeholder=l_(u'First'),
            validator=validators.ByteString(min=5, max=5),
            required=True,
            maxlength=5,
            # attrs={
            #     'autofocus': True
            # },
            css_class="form-control font-monospace fs-6 text-uppercase"
        )

        second_word = twf.TextField(
            label=l_(u'Second word'),
            help_text=l_(u'Please Enter Wednesday challenge second word (required)'),
            placeholder=l_(u'Second'),
            validator=validators.ByteString(min=5, max=5),
            required=True,
            maxlength=5,
            css_class="form-control font-monospace fs-6 text-uppercase"
        )

        third_word = twf.TextField(
            label=l_(u'Third word'),
            help_text=l_(u'Please Enter Wednesday challenge third word (required)'),
            placeholder=l_(u'Third'),
            validator=validators.ByteString(min=5, max=5),
            required=True,
            maxlength=5,
            css_class="form-control font-monospace fs-6 text-uppercase"
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

    action = lurl('/save_wednesday_challenge_words')

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


class UserRegistration(twf.Form):
    css_class = 'clearfix'

    class child(twf.TableLayout):
        css_class = 'table table-borderless'

        user_name = twf.TextField(
            label=l_('User Name'),
            help_text=l_(
                u"Allowed characters are a-z and A-Z (basic latin), 0-9, dot, underscore, minus and plus. First character can't be dot or plus"),
            validator=UniqueUserValidator(not_empty=True),
            css_class="form-control",
            placeholder=l_('User Name'),
            autofocus=True
        )

        email_address = twf.TextField(
            label=l_('Email'),
            help_text=l_(
                u"Your email for sending confirmation link and for the possibility of resetting a forgotten password"),
            validator=UniqueEmailValidator(not_empty=True),
            css_class="form-control",
            placeholder=l_('Email')
        )

        password = twf.PasswordField(
            label=l_('Password'),
            help_text=l_(u"Choose a strong enough password for your security or let browser do suggested password"),
            validator=twc.Required,
            css_class="form-control",
            placeholder=l_('Password')
        )

        password_confirm = twf.PasswordField(
            label=l_('Confirm Password'),
            help_text=l_(u"Enter same password again, to ensure that it is entered correctly without typos"),
            validator=twc.Required,
            css_class="form-control",
            placeholder=l_('Confirm Password')
        )

    validator = validators.FieldsMatch('password', 'password_confirm')

    attrs = {'role': 'form'}

    submit = twf.SubmitButton(
        value=l_(u'Register'),
        css_class='btn btn-outline-secondary btn-lg float-end'
    )


class NewPasswordForm(twf.Form):
    css_class = 'clearfix'

    class child(twf.TableLayout):
        css_class = 'table table-borderless'

        data = twf.HiddenField()

        password = twf.PasswordField(
            label=l_('New password'),
            validator=twc.Validator(required=True),
            css_class="form-control",
            placeholder=l_('New password'),
            autofocus=True
        )

        password_confirm = twf.PasswordField(
            label=l_('Confirm new password'),
            validator=twc.Validator(required=True),
            css_class="form-control",
            placeholder=l_('Confirm new password')
        )

    validator = validators.FieldsMatch('password', 'password_confirm')

    submit = twf.SubmitButton(
        value=l_(u'Save new password'),
        css_class='btn btn-outline-secondary btn-lg float-end'
    )


class ResetPasswordForm(twf.Form):
    class child(twf.TableLayout):
        css_class = 'table table-borderless'

        email_address = twf.TextField(
            label=l_('Email address'),
            validator=RegisteredUserValidator(required=True),
            css_class="form-control",
            placeholder=l_('Email address'),
            autofocus=True
        )

    submit = twf.SubmitButton(
        value=l_('Send Request'),
        css_class='btn btn-outline-secondary btn-lg float-end'
    )


class UserProfileEditForm(twf.Form):
    class child(twf.TableLayout):
        css_class = 'table table-borderless'

        email_address = twf.TextField(
            label=l_('Email Address'),
            validator=RegisteredUserValidator(required=True),
            css_class="form-control",
            placeholder=l_('Email Address'),
            autofocus=True
        )

        display_name = twf.TextField(
            label=l_('Display Name'),
            # help_text=l_(u'Enter new User Name'),
            validator=UniqueUserValidator(not_empty=True),
            css_class="form-control",
            placeholder=l_('Display Name')
        )

    submit = twf.SubmitButton(
        value=l_('Save'),
        css_class='btn btn-light btn-lg'
    )


class UserProfileChangePasswordForm(twf.Form):
    class child(twf.TableLayout):
        css_class = 'table table-borderless'

        password = twf.PasswordField(
            label=l_('Password'),
            validator=twc.Validator(required=True),
            css_class="form-control",
            placeholder=l_('New password'),
            autofocus=True
        )

        verify_password = twf.PasswordField(
            label=l_('Confirm Password'),
            validator=twc.Validator(required=True),
            css_class="form-control",
            placeholder=l_('Confirm new password')
        )

    validator = validators.FieldsMatch('password', 'verify_password')

    submit = twf.SubmitButton(
        value=l_(u'Save'),
        css_class='btn btn-light btn-lg'
    )
