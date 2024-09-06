# -*- coding: utf-8 -*-
"""X/Twitter controller module"""

from tg import expose, redirect, validate, flash, url, require, tmpl_context, config, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
# from tg import predicates
from tg.predicates import has_any_permission

from lustitelskadb.lib.base import BaseController
# from lustitelskadb.model import DBSession

from requests_oauthlib import OAuth1Session

import lustitelskadb.lib.forms as appforms

__all__ = ['XTwitterController']


class XTwitterController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()

    @expose('lustitelskadb.templates.administration.xtwitter.index')
    @require(has_any_permission('manage', 'xtwitter', msg=l_('Only for users with appropriate permissions')))
    def index(self, **kw):
        """X/Twitter administration frontpage."""
        tmpl_context.form = appforms.XTwitterPostForm()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value
        else:
            tmpl_context.form.value = kw

        return dict(page='admin-xtwitter-index')

    @expose()
    @validate(form=appforms.XTwitterPostForm(), error_handler=index)
    @require(has_any_permission('manage', 'xtwitter', msg=l_('Only for users with appropriate permissions')))
    def create_post(self, **kw):
        """Create post on X/Twitter"""
        oauth = OAuth1Session(
            config.get('xtwitter.consumer_key', ''),
            client_secret=config.get('xtwitter.consumer_secret', ''),
            resource_owner_key=config.get('xtwitter.access_key', ''),
            resource_owner_secret=config.get('xtwitter.access_secret', ''),
        )

        response = oauth.post(
            "https://api.x.com/2/tweets",
            json={
                'text': kw.get('text', '')
            }
        )

        if response.ok:
            flash(_(u"Post successfully sent to X/Twitter."))
            return redirect('/admin/xtwitter')
        else:
            flash(_(u"Something went wrong, during sending post to X/Twitter. Error Code: {}").format(response.status_code), 'error')
            return redirect('/admin/xtwitter', params=kw)
