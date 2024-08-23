# -*- coding: utf-8 -*-
"""Main Controller"""

import logging
from numba.cuda import args
log = logging.getLogger(__name__)

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context, validate
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from tg.decorators import paginate

from lustitelskadb import model
from lustitelskadb.controllers.admin import AdministrationController
from lustitelskadb.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from lustitelskadb.lib.base import BaseController
from lustitelskadb.controllers.error import ErrorController

import lustitelskadb.lib.forms as appforms

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the LustitelskaDB application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    admin = AdministrationController()
    dbadmin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "LustitelskaDB"

        tmpl_context.pager_params = dict(
            format=u"$link_first $link_previous ~2~ $link_next $link_last",
            symbol_first=u"«",
            symbol_last=u"»",
            symbol_previous=u"‹",
            symbol_next=u"›",
            dotdot_attr={'class': 'page-item'},
            link_attr={'class': 'page-link'},
            curpage_attr={'class':'page-item active', 'aria-current': 'page'},
            page_link_template=u'<li class="page-item"><a%s>%s</a></li>',
            page_plain_template=u'<li%s><a class="page-link">%s</a></li>'
        )

    @expose('lustitelskadb.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('lustitelskadb.templates.newresult')
    def newresult(self, **kw):
        """Handle page with registering new user game result."""
        tmpl_context.form = appforms.ResultForm()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value

        return dict(page='newresult')

    @expose()
    @validate(form=appforms.ResultForm(), error_handler=newresult)
    def save_result(self, **kw):
        """Save result."""
        flash(l_(u"Result successfully added"))
        return redirect('/')

    @expose('lustitelskadb.templates.libriciphers')
    @paginate('libriciphers', items_per_page=1)
    def libriciphers(self, *args):
        """Handle LibriCiphers game"""
        libriciphers = DBSession.query(model.LibriCipher)
        if len(args):
            if args[0].isnumeric():
                libriciphers = libriciphers.filter(model.LibriCipher.uid == args[0])
        libriciphers = libriciphers.order_by(model.LibriCipher.uid.desc())

        return dict(page='libriciphers', libriciphers=libriciphers)

    @expose('lustitelskadb.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('lustitelskadb.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)
