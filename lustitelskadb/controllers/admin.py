# -*- coding: utf-8 -*-
"""Administration controller module."""

import logging
log = logging.getLogger(__name__)

from tg import expose, redirect, validate, flash, url, require, tmpl_context, config, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import has_permission, has_any_permission

from lustitelskadb.controllers.libricipher import LibriCipherController
from lustitelskadb.controllers.xtwitter import XTwitterController

from lustitelskadb.lib.base import BaseController

from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.layouts import GroupedBootstrapAdminLayout
from tgext.admin.config import CrudRestControllerConfig
from tgext.admin.controller import AdminController
from tgext.crud import EasyCrudRestController

from lustitelskadb import model
from lustitelskadb.model import DBSession

import lustitelskadb.lib.forms as appforms
from lustitelskadb.lib.utils import assemble_game_scoresheet

from pathlib import Path
from datetime import datetime, timedelta
import csv
import requests

import tw2.core as twc
import tw2.forms as twf

from lustitelskadb.lib.injects import closing_deadline_jssrc, emojipicker_init_jssrc
from lustitelskadb.lib.utils import today_game_no

__all__ = ['AdministrationController']


class CustomCheckbox(twf.CheckBox):

    css_class = "form-check-input h4"


class XTwitterAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'SNS'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'user_info',
                'results'
            ]
        }

        __form_options__ = {
            '__omit_fields__': [
                'user_info',
                'results'
            ]
        }


class GameAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Game'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'post_xid'
            ]
        }

        __form_edit_options__ = {
            '__omit_fields__': [
                'post_xid',
                'created',
                'updated',
            ]
        }

        __form_new_options__ = {
            '__omit_fields__': [
                'uid',
                'post_xid',
                'created',
                'updated'
            ]
        }


class GameResultsAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Game'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'game_raw_data'
            ]
        }

        __form_edit_options__ = {
            '__omit_fields__': [
                'created',
                'updated',
            ],
            '__field_widgets__': {
                'wednesday_challenge': CustomCheckbox(
                    key="wednesday_challenge",
                    label="Wednesday challenge"
                )
            }
        }

        __form_new_options__ = {
            '__omit_fields__': [
                'uid',
                'created',
                'updated'
            ],
            '__field_widgets__': {
                'wednesday_challenge': CustomCheckbox(
                    key="wednesday_challenge",
                    label="Wednesday challenge"
                )
            }
        }

        @expose(inherit=True)
        def post(self, *args, **kw):
            kw['user_id'] = kw.pop('user')
            if kw['wednesday_challenge'] == False and kw['game_no'] % 7 != 5:
                kw['wednesday_challenge'] = None
            return EasyCrudRestController.post(self, *args, **kw)

        @expose(inherit=True)
        def put(self, *args, **kw):
            kw['user_id'] = kw.pop('user')
            if kw['wednesday_challenge'] == False and kw['game_no'] % 7 != 5:
                kw['wednesday_challenge'] = None
            return EasyCrudRestController.put(self, *args, **kw)


class WednesdayChallengesWordsAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Game'

    class defaultCrudRestController(EasyCrudRestController):
        # __table_options__ = {
        #     '__omit_fields__': [
        #     ]
        # }

        __form_edit_options__ = {
            '__omit_fields__': [
                'created',
                'updated',
            ]
        }

        __form_new_options__ = {
            '__omit_fields__': [
                'uid',
                'created',
                'updated'
            ]
        }

        @expose(inherit=True)
        def post(self, *args, **kw):
            kw['user_id'] = kw.pop('user')
            return EasyCrudRestController.post(self, *args, **kw)

        @expose(inherit=True)
        def put(self, *args, **kw):
            kw['user_id'] = kw.pop('user')
            return EasyCrudRestController.put(self, *args, **kw)


class ClanAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Clan'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'members'
            ]
        }

        __form_options__ = {
            '__omit_fields__': [
                'members'
            ]
        }


class ClanMemberAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Clan'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'clan_id',
                'user_id'
            ]
        }

        __form_options__ = {
            '__omit_fields__': [
                'uid',
                'clan_id',
                'user_id'
            ]
        }


class UserAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Users and Groups'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                '_password',
                'password',
                'results',
                'wednesday_challenges'
            ]
        }

        __form_edit_options__ = {
            '__omit_fields__': [
                '_password',
                'created',
                'results',
                'wednesday_challenges'
            ]
        }

        __form_new_options__ = {
            '__omit_fields__': [
                '_password',
                'created',
                'results',
                'wednesday_challenges'
            ]
        }

        @expose(inherit=True)
        def post(self, *args, **kw):
            kw['xtwitter_uid'] = kw.pop('xuser')
            return EasyCrudRestController.post(self, *args, **kw)

        @expose(inherit=True)
        def put(self, *args, **kw):
            kw['xtwitter_uid'] = kw.pop('xuser')
            return EasyCrudRestController.put(self, *args, **kw)


class GroupAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Users and Groups'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'group_id',
                'created',
                'users'
            ]
        }

        __form_edit_options__ = {
            '__omit_fields__': [
                'group_id',
                'created',
                'users'
            ]
        }

        __form_new_options__ = {
            '__omit_fields__': [
                'group_id',
                'created',
                'users'
            ]
        }

        @expose(inherit=True)
        def post(self, *args, **kw):
            return EasyCrudRestController.post(self, *args, **kw)

        @expose(inherit=True)
        def put(self, *args, **kw):
            return EasyCrudRestController.put(self, *args, **kw)


class PermissionAdminCrudConfig(CrudRestControllerConfig):

    admin_group = 'Users and Groups'

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': [
                'permission_id'
            ]
        }

        __form_edit_options__ = {
            '__omit_fields__': [
            ]
        }

        __form_new_options__ = {
            '__omit_fields__': [
            ]
        }

        @expose(inherit=True)
        def post(self, *args, **kw):
            return EasyCrudRestController.post(self, *args, **kw)

        @expose(inherit=True)
        def put(self, *args, **kw):
            return EasyCrudRestController.put(self, *args, **kw)


class CustomGroupedBootstrapAdminLayout(GroupedBootstrapAdminLayout):

    template_index = 'lustitelskadb.templates.tgext.admin.bootstrap_grouped_index'

    crud_templates = {
        'get_all': [
            'kajiki:lustitelskadb.templates.tgext.admin.bootstrap_crud.get_all'
        ],
        'edit': [
            'kajiki:lustitelskadb.templates.tgext.admin.bootstrap_crud.edit'
        ],
        'new': [
            'kajiki:lustitelskadb.templates.tgext.admin.bootstrap_crud.new'
        ]
    }


class CustomAdminConfig(TGAdminConfig):

    project_name = "LustitelskaDB"

    layout = CustomGroupedBootstrapAdminLayout

    include_left_menu = False

    xtwitter = XTwitterAdminCrudConfig

    game = GameAdminCrudConfig

    gameresult = GameResultsAdminCrudConfig

    wednesdaychallengeword = WednesdayChallengesWordsAdminCrudConfig

    clan = ClanAdminCrudConfig

    clanmember = ClanMemberAdminCrudConfig

    user = UserAdminCrudConfig

    group = GroupAdminCrudConfig

    permission = PermissionAdminCrudConfig


class AdministrationController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = not_anonymous()

    dbadmin = AdminController(model, DBSession, config_type=CustomAdminConfig)

    libricipher = LibriCipherController()

    xtwitter = XTwitterController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "LustitelskaDB"

    @expose('lustitelskadb.templates.administration.index')
    @require(has_any_permission('manage', 'dashboard', msg=l_('Only for users with appropriate permissions')))
    def index(self, **kw):
        return dict(page='administration/index', restart_confirmation_msg=_('Do you really want restart application? This will be done immediately!'))

    @expose('lustitelskadb.templates.administration.result')
    @require(has_any_permission('manage', 'resultsadmin', msg=l_('Only for users with appropriate permissions')))
    def result(self, **kw):
        """Create/Edit game result."""
        tmpl_context.form = appforms.ResultAdminForm()

        if today_game_no() % 7 == 5:
            tmpl_context.form.child.children.wednesday_challenge.container_attrs = {
                'style': 'color: var(--bs-danger);'
            }
            tmpl_context.form.child.children.wednesday_challenge.required = True

        users = DBSession.query(model.User).all()
        tmpl_context.form.child.children.user_id.options = [(user.user_id, u"{} @{}".format(user.display_name, user.user_name)) for user in users]

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value
        else:
            tmpl_context.form.value = dict()

        emoji_picker_jslnk = twc.JSLink(
            location="bodybottom",
            type="module",
            link="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js",
            template='kajiki:lustitelskadb.templates.tw2.core.jslink'
        )

        emoji_picker_jslnk.inject()
        emojipicker_init_jssrc.inject()

        return dict(page='administration/result')

    @expose()
    @require(has_any_permission('manage', 'resultsadmin', msg=l_('Only for users with appropriate permissions')))
    @validate(form=appforms.ResultAdminForm(), error_handler=result)
    def save_result(self, **kw):
        """Save result."""
        parsed_vals = {
            'game_no': None,
            'step': None,
            'time': None
        }
        sp_result = kw.get('game_result', '').split()
        for s in sp_result:
            if s.find('#den') != -1:
                parsed_vals['game_no'] = int(s.lstrip('#den')) if s.lstrip('#den').isdigit() else None
            elif s.find('#krok') != -1:
                parsed_vals['step'] = int(s.lstrip('#krok')) if s.lstrip('#krok').isdigit() else None
        if sp_result[-2].endswith('min') and sp_result[-1].endswith('s'):
            parsed_vals['time'] = int(sp_result[-2].rstrip('min')) * 60 + int(sp_result[-1].rstrip('s')) if sp_result[-2].rstrip('min').isdigit() and sp_result[-1].rstrip('s').isdigit() else None

        # Unicorns has no time in result
        if parsed_vals['step'] == 1 and parsed_vals['time'] == None:
            parsed_vals['time'] == 0

        game_result = DBSession.query(model.GameResult)
        game_result = game_result.filter(
            model.GameResult.game_no == parsed_vals['game_no'],
            model.GameResult.user_id == kw.get('user_id')
        ).first()

        if game_result:
            flash(_(u"Result of this user game is already in database"), 'warning')
            redirect('/admin')

        game_result = model.GameResult(
            user_id=kw.get('user_id', None),
            game_no=parsed_vals['game_no'],
            game_time=timedelta(seconds=parsed_vals['time']) if parsed_vals['time'] != None else None,
            game_rows=parsed_vals['step'],
            wednesday_challenge=kw.get('wednesday_challenge', None) if parsed_vals['game_no'] % 7 == 5 else None,
            comment=kw.get('comment', None) if kw.get('comment', None) else None,
            game_result_time=timedelta(seconds=parsed_vals['time'] + (parsed_vals['step'] - 1) * 12) if parsed_vals['time'] != None and parsed_vals['step'] else None,
            game_raw_data=kw.get('game_result', None)
        )

        DBSession.add(game_result)

        try:
            DBSession.flush()
            DBSession.refresh(game_result)
        except Exception as e:
            flash(_(u"Something went wrong! Can't save game result to database!"), 'error')
            redirect('/')

        assemble_game_scoresheet(parsed_vals['game_no'])

        flash(l_(u"Your result has been successfully saved to database"))

        return redirect('/admin')

    @expose('lustitelskadb.templates.administration.importlegacydata')
    @require(has_any_permission('manage', 'legacyimport', msg=l_('Only for users with appropriate permissions')))
    def legacyimport(self, **kw):
        """Import legacy data."""
        tmpl_context.form = appforms.LegacyDataImportForm()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value

        return dict(page='administration/legacyimport')

    @expose()
    @require(has_any_permission('manage', 'legacyimport', msg=l_('Only for users with appropriate permissions')))
    @validate(form=appforms.LegacyDataImportForm(), error_handler=legacyimport)
    def process_legacy_import(self, **kw):
        """Process Legacy Import."""
        if 'csv_file' not in kw:
            flash(_(u"Missing CSV file for import"))
            redirect('/admin')

        with open(u'/tmp/{}'.format(kw.get('csv_file').filename), 'wb') as f:
            f.write(kw.get('csv_file').file.read())

        with open(u'/tmp/{}'.format(kw.get('csv_file').filename), 'r') as f:
            reader = csv.DictReader(f)

            statistics = {
                'all_count': 0,
                'imported_count': 0,
                'duplicity_skipped': 0,
                'added_nicknames': 0
            }
            parsed_vals = {}

            try:
                for row in reader:
                    statistics['all_count'] += 1
                    for key in parsed_vals:
                        parsed_vals[key] = None

                    sp_result = row[config.get('legacyimport.colname.result')].split()
                    for s in sp_result:
                        if s.find('#den') != -1:
                            parsed_vals['game_no'] = int(s.lstrip('#den'))
                        elif s.find('#krok') != -1:
                            parsed_vals['step'] = int(s.lstrip('#krok'))
                    if sp_result[-2].endswith('min') and sp_result[-1].endswith('s'):
                        parsed_vals['time'] = int(sp_result[-2].rstrip('min')) * 60 + int(sp_result[-1].rstrip('s'))

                    xuser = DBSession.query(model.XTwitter).filter(model.XTwitter.user_name == row[config.get('legacyimport.colname.nickname')]).first()
                    if not xuser:
                        xuser = model.XTwitter(
                            xid=row[config.get('legacyimport.colname.nickname')],
                            user_name=row[config.get('legacyimport.colname.nickname')],
                            display_name=row[config.get('legacyimport.colname.nickname')]
                        )
                        DBSession.add(xuser)
                        DBSession.flush()
                        DBSession.refresh(xuser)
                        statistics['added_nicknames'] += 1

                    game = DBSession.query(model.GameResult, model.XTwitter).join(model.XTwitter, model.XTwitter.uid == model.GameResult.xtwitter_uid)
                    game = game.filter(
                        model.GameResult.game_no == parsed_vals['game_no'],
                        model.GameResult.game_time == parsed_vals['time'],
                        model.GameResult.game_rows == parsed_vals['step'],
                        model.GameResult.comment == row[config.get('legacyimport.colname.comment')] if row[config.get('legacyimport.colname.comment')] else None,
                        model.GameResult.created == datetime.strptime(row[config.get('legacyimport.colname.created')], "%d.%m.%Y %H:%M:%S")
                    ).first()

                    if game:
                        statistics['duplicity_skipped'] += 1
                    else:
                        game = model.GameResult(
                            game_no=parsed_vals['game_no'],
                            game_time=timedelta(seconds=parsed_vals['time']) if parsed_vals['time'] else None,
                            game_rows=parsed_vals['step'],
                            wednesday_challenge={'': None, '✅': True, '❎': False}[row[config.get('legacyimport.colname.wednesdaychallenge')]],
                            comment=row[config.get('legacyimport.colname.comment')],
                            game_result_time=timedelta(seconds=parsed_vals['time'] + (parsed_vals['step'] - 1) * 12) if parsed_vals['time'] and parsed_vals['step'] else None,
                            game_raw_data=row[config.get('legacyimport.colname.result')],
                            created=datetime.strptime(row[config.get('legacyimport.colname.created')], "%d.%m.%Y %H:%M:%S"),
                            xtwitter=xuser
                        )
                        DBSession.add(game)
                        DBSession.flush()
                        statistics['imported_count'] += 1
                flash(_(u"The import was successful. {all_count} records processed, {imported_count} records imported, {duplicity_skipped} duplicate records skipped, and {added_nicknames} ; added.").format(**statistics))
            except Exception as e:
                flash(_(u'The import attempt ended with an error: "{}"').format(e))

        redirect('/admin')

    @expose()
    @require(has_any_permission('manage', 'legacyimport', msg=l_('Only for users with appropriate permissions')))
    def reassemble_scoresheet(self, **kw):
        """Reassemble score sheet."""
        games_nums = DBSession.query(model.GameResult.game_no).order_by(model.GameResult.game_no).distinct()

        for game_no in games_nums:
            assemble_game_scoresheet(game_no.game_no, dbflush=False)

        flash(_(u'Score Sheet successfully reassembled for {} games').format(games_nums.count()))
        DBSession.flush()

        redirect('/admin')

    @expose('lustitelskadb.templates.administration.restart')
    @require(has_any_permission('manage', 'restartapp', msg=l_('Only for users with appropriate permissions')))
    def restartapp(self, **kw):
        """Restart APP page."""
        restart_progress_jss = twc.JSSource(src='''
        "use strict";
        function restartProgress(percent=0) {
            if (percent > 100) return;

            $('#restartapp_progress_bar>.progress-bar').css('width', percent + '%%').attr('aria-valuenow', percent);

            if (percent < 100) {
                percent += 1;
                setTimeout(() => {
                    restartProgress(percent);
                }, 250);
            } else {
                window.location.href = "%(redirect_url)s";
            }
        }

        $(() => {
            $.ajax({
              url: "%(exec_restart_url)s",
              context: document.body
            }).always(() => {
                restartProgress();
            });
        });
        ''' % dict(redirect_url=url('/admin'), exec_restart_url=url('/admin/exec_restart')))

        restart_progress_jss.inject()
        return dict(page='administration/restartapp')

    @expose()
    @require(has_any_permission('manage', 'restartapp', msg=l_('Only for users with appropriate permissions')))
    def exec_restart(self, **kw):
        """Execute restart app"""

        flash(l_("Application successfully restarted"))
        Path(config.get('app.restart.semaphore', 'development.ini')).touch()
