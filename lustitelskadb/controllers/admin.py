# -*- coding: utf-8 -*-
"""Administration controller module."""

import logging
log = logging.getLogger(__name__)

from tg import expose, redirect, validate, flash, url, require, tmpl_context, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import has_permission, has_any_permission

from lustitelskadb.controllers.libricipher import LibriCipherController

from lustitelskadb.lib.base import BaseController
# from lustitelskadb.model import DBSession

from pathlib import Path

import tw2.core as twc

__all__ = ['AdministrationController']


class AdministrationController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = not_anonymous()

    libricipher = LibriCipherController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "LustitelskaDB"

    @expose('lustitelskadb.templates.administration.index')
    @require(has_any_permission('manage', 'dashboard', msg=l_('Only for users with appropriate permissions')))
    def index(self, **kw):
        return dict(page='administration/index', restart_confirmation_msg = _('Do you really want restart application? This will be done immediately!'))

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
