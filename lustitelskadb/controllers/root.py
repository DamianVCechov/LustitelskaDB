# -*- coding: utf-8 -*-
"""Main Controller"""

import logging
log = logging.getLogger(__name__)

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context, validate, session, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from tg.decorators import paginate

from lustitelskadb import model
from lustitelskadb.controllers.admin import AdministrationController
from lustitelskadb.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from requests_oauthlib import OAuth1Session

try:
    import ujson as json
except (ImportError, ModuleNotFoundError, SyntaxError):
    try:
        import simplejson as json
    except (ImportError, ModuleNotFoundError, SyntaxError):
        try:
            import json
        except:
            log.error("Any of known JSON module not available (ujson, simplejson, json)")

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

    @expose()
    def xauthorize(self, **kw):
        """Authorize via X/Twitter."""
        if not session.has_key('xauthorized.redirect.url'):
            flash(_("Unknown source for authorization, canceled"))
            redirect('/')

        if session.has_key('me_on_xtwitter'):
            return redirect(url('/xauthorized'))

        oauth = OAuth1Session(
            config.get('xtwitter.consumer_key', ''),
            client_secret=config.get('xtwitter.consumer_secret', '')
        )

        try:
            fetch_response = oauth.fetch_request_token(config.get('xtwitter.request_token_url', "https://api.x.com/oauth/request_token"))
        except ValueError:
            log.error("There may have been an issue with the consumer_key or consumer_secret you entered.")
            flash(_(u"There may have been an issue with the consumer_key or consumer_secret in application"))
            return redirect('/xerror')

        session['resource_owner_key'] = fetch_response.get("oauth_token")
        session['resource_owner_secret'] = fetch_response.get("oauth_token_secret")
        session.save()

        log.debug("Got OAuth token: %s" % session['resource_owner_key'])

        return redirect(oauth.authorization_url(config.get('twittertools.base_authorization.url', "https://api.x.com/oauth/authorize")))

    @expose()
    def xauthorized(self, **kw):
        """Callback URL when is authorized via X/Twitter."""
        if kw.has_key('denied'):
            redirect('/xdenied', params=kw)

        oauth = OAuth1Session(
            config.get('xtwitter.consumer_key', ''),
            client_secret=config.get('xtwitter.consumer_secret', ''),
            resource_owner_key=session.get('resource_owner_key'),
            resource_owner_secret=session.get('resource_owner_secret'),
            verifier=kw.get('oauth_verifier')
        )
        oauth_tokens = oauth.fetch_access_token(config.get('xtwitter.access_token.url', "https://api.x.com/oauth/access_token"))

        session['access_token'] = oauth_tokens["oauth_token"]
        session['access_token_secret'] = oauth_tokens["oauth_token_secret"]

        # User fields are adjustable, options include:
        # created_at, description, entities, id, location, most_recent_tweet_id,
        # name, pinned_tweet_id, profile_image_url, protected,
        # public_metrics, url, username, verified, verified_type and withheld

        fields = "created_at,description,entities,id,location,most_recent_tweet_id,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type,withheld"
        params = {
            "user.fields": fields
        }

        response = oauth.get("https://api.x.com/2/users/me", params=params)

        if response.status_code != 200:
            log.error("Request returned an error: {} {}".format(response.status_code, response.text))
            flash(_(u"Can't get user info from Twitter"))
            session.delete()
            redirect('/xerror')

        session['me_on_xtwitter'] = response.json()
        del(session['resource_owner_key'])
        del(session['resource_owner_secret'])
        session.save()

        log.debug(json.dumps(response.json(), indent=4, sort_keys=True))

        if session.has_key('xauthorized.redirect.url'):
            flash(_("Successfully authorized"))
            return redirect(session.get('xauthorized.redirect.url'))
        else:
            flash(_("Succesfully authorized, but missing landing URL"))
            return redirect('/')

    @expose('lustitelskadb.templates.xdenied')
    def xdenied(self, **kw):
        """Landing URL when user denied authorization."""
        return dict(page='xerror', denied=kw.get('denied', None))

    @expose('lustitelskadb.templates.xerror')
    def xerror(self, **kw):
        """Landing URL when error raised while authentication via X/Twitter."""
        return dict(page='xerror')

    @expose()
    def xdetach(self, **kw):
        """Detach authorization from Twitter"""
        session.delete()
        flash(_("Successfully detached from X/Twitter"))
        return redirect('/')

    @expose('lustitelskadb.templates.newresult')
    def newresult(self, **kw):
        """Handle page with registering new user game result."""
        tmpl_context.form = appforms.ResultForm()

        if not session.has_key('me_on_xtwitter'):
            session['xauthorized.redirect.url'] = url('/newresult')
            session.save()
            redirect('/xauthorize')
        else:
            if session.has_key('xauthorized.redirect.url'):
                del(session['xauthorized.redirect.url'])
                session.save()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value
        else:
            tmpl_context.form.value = {
                'xtwitter_uid': session['me_on_xtwitter']['data']['id'],
                'xtwitter_username': session['me_on_xtwitter']['data']['username'],
                'xtwitter_displayname': session['me_on_xtwitter']['data']['name']
            }

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
            if args[0].isdigit():
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
