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

from pathlib import Path
from datetime import datetime, timedelta
import csv
import requests

import tw2.core as twc

__all__ = ['AdministrationController']


class XTwitterAdminCrudConfig(CrudRestControllerConfig):

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': ['user_info', 'results']
        }


class GameResultsAdminCrudConfig(CrudRestControllerConfig):

    class defaultCrudRestController(EasyCrudRestController):
        __table_options__ = {
            '__omit_fields__': ['game_raw_data']
        }


class CustomAdminConfig(TGAdminConfig):

    layout = GroupedBootstrapAdminLayout

    include_left_menu = False

    xtwitter = XTwitterAdminCrudConfig

    gameresult = GameResultsAdminCrudConfig


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
                            game_time=timedelta(seconds=parsed_vals['time']) if parsed_vals['time'] and parsed_vals['step'] else None,
                            game_rows=parsed_vals['step'],
                            comment=row[config.get('legacyimport.colname.comment')],
                            game_result_time=timedelta(seconds=parsed_vals['time'] + (parsed_vals['step'] - 1) * 12) if parsed_vals['time'] and parsed_vals['step'] else None,
                            game_raw_data=row[config.get('legacyimport.colname.result')],
                            created=datetime.strptime(row[config.get('legacyimport.colname.created')], "%d.%m.%Y %H:%M:%S"),
                            xtwitter=xuser
                        )
                        DBSession.add(game)
                        DBSession.flush()
                        statistics['imported_count'] += 1
                flash(_(u"The import was successful. {all_count} records processed, {imported_count} records imported, {duplicity_skipped} duplicate records skipped, and {added_nicknames} users added.").format(**statistics))
            except Exception as e:
                flash(_(u'The import attempt ended with an error: "{}"').format(e))

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
