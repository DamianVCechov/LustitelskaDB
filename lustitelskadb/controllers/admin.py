# -*- coding: utf-8 -*-
"""Administration controller module."""

from tg import expose, redirect, validate, flash, url, require
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import has_permission, has_any_permission

from lustitelskadb.lib.base import BaseController
# from lustitelskadb.model import DBSession

__all__ = ['AdministrationController']


class AdministrationController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = not_anonymous()

    @expose('lustitelskadb.templates.admin')
    @require(has_any_permission('manage', 'dashboard', msg=l_('Only for users with appropriate permissions')))
    def index(self, **kw):
        return dict(page='administration-index')
