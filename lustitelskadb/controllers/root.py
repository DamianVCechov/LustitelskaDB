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
from lustitelskadb.model import DBSession

from sqlalchemy.sql.expression import func

import tw2.core as twc

import requests
from requests_oauthlib import OAuth1Session, OAuth2Session

import random
import string
from datetime import timedelta

# Python 2 compatibility hack
try:
    ModuleNotFoundError
except:
    ModuleNotFoundError = ImportError

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
from lustitelskadb.controllers.admin import AdministrationController
from lustitelskadb.controllers.api import APIController

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

    api = APIController()

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
        comments = DBSession.query(model.GameResult).filter(model.GameResult.comment != None, model.GameResult.comment != '').order_by(func.random()).limit(100).all()

        last_games = []
        last_game_nums = DBSession.query(model.GameResult.game_no).order_by(model.GameResult.game_no.desc()).distinct().limit(2).all()
        for lg in last_game_nums:
            game = DBSession.query(model.GameResult)
            game = game.filter(model.GameResult.game_no == lg.game_no)
            if lg.game_no % 7 == 5:
                game = game.order_by(model.GameResult.game_result_time == None, model.GameResult.wednesday_challenge.desc(), model.GameResult.game_result_time, model.GameResult.game_rows)
            else:
                game = game.order_by(model.GameResult.game_result_time == None, model.GameResult.game_result_time, model.GameResult.game_rows)
            last_games.append(game.all())

        closing_deadline_jssrc = twc.JSSource(src='''"use strict";
            function setClosingProgressBar() {
                let now = new Date();
                let target = new Date(now);
                let dayInMillisec = 24 * 60 * 60 * 1000;
                let leftPercent = 0;

                target.setHours(18);
                target.setMinutes(0);
                target.setSeconds(0);
                target.setMilliseconds(0);

                if (now.getHours() >= 18) {
                    target = new Date(target.getTime() + dayInMillisec);
                }

                leftPercent = ((target - now) / dayInMillisec) * 100;

                $('#closingDeadlineProgress.progress').attr('aria-value-now', Math.round(leftPercent));
                $('#closingDeadlineProgress.progress>.progress-bar').width(String(100 - Math.round(leftPercent)) + '%');
                if (leftPercent > 50) {
                    $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-success').removeClass('bg-warning').removeClass('bg-danger');
                } else if (leftPercent > 25) {
                    $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-warning').removeClass('bg-success').removeClass('bg-danger');
                } else {
                    $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-danger').removeClass('bg-success').removeClass('bg-warning');
                }

                setTimeout(setClosingProgressBar, 1000);
            }

            $(() => {
                setClosingProgressBar();
            });
        ''')
        closing_deadline_jssrc.inject();

        return dict(page='index', comments=comments, last_game_nums=last_game_nums, last_games=last_games)

    @expose('lustitelskadb.templates.detail')
    def detail(self, uid=None, *args, **kw):
        """Detail of user game result."""
        if not uid:
            flash(_("Missing unique ID of user game result"))
            return redirect('/')

        gameresult = DBSession.query(model.GameResult).filter(model.GameResult.uid == uid).first()
        if not gameresult:
            flash(_("Requested user game result not found"))
            return redirect('/')

        return dict(page="detail", gameresult=gameresult)

    @expose()
    def xauthorize(self, **kw):
        """Authorize via X/Twitter."""
        if not session.has_key('xauthorized.redirect.url'):
            flash(_("Unknown source for authorization, canceled"))
            redirect('/')

        if session.has_key('me_on_xtwitter'):
            return redirect(url('/xauthorized'))

        if config.get('xtwitter.oauth.type', 'oauth1').lower() == 'oauth1':
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
        elif config.get('xtwitter.oauth.type', 'oauth1').lower() == 'oauth2':
            oauth = OAuth2Session(
                client_id=config.get('xtwitter.client_id', ''),
                scope=['users.read', 'tweet.read'],
                redirect_uri=url('/xauthorized', qualified=True)
            )

            challenge = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(64))
            session.save()

            authorization_url, state = oauth.authorization_url(
                config.get('xtwitter.base_authorization.oauth2.url', "https://twitter.com/i/oauth2/authorize"),
                code_challenge=challenge,
                code_challenge_method='plain'
            )

            session['xoauth2_challenge'] = challenge
            session['xoauth2_state'] = state
            session.save()

            return redirect(authorization_url)
        else:
            flash(_(u"Unknown type of OAuth in config"), 'error')

            if session.has_key('xauthorized.redirect.url'):
                del(session['xauthorized.redirect.url'])
                session.save()

            return redirect('/')

    @expose()
    def xauthorized(self, **kw):
        """Callback URL when is authorized via X/Twitter."""
        if 'denied' in kw or kw.get('error', None) == 'access_denied':
            redirect('/xdenied', params=kw)

        if config.get('xtwitter.oauth.type', 'oauth1').lower() == 'oauth1':

            if not session.has_key('resource_owner_key') or not session.has_key('resource_owner_secret'):
                flash(_(u"I cannot find the keys needed to continue "
                        u"in authorization process in the session. "
                        u"Maybe you are using a light version of "
                        u"the browser that cannot maintain a session "
                        u"or you have disabled the saving of cookies. "
                        u"Try to switch to a full-fledged browser or "
                        u"turn on the saving of cookies."), 'warning')
                redirect('/')

            oauth = OAuth1Session(
                config.get('xtwitter.consumer_key', ''),
                client_secret=config.get('xtwitter.consumer_secret', ''),
                resource_owner_key=session.get('resource_owner_key', ''),
                resource_owner_secret=session.get('resource_owner_secret', ''),
                verifier=kw.get('oauth_verifier')
            )
            oauth_tokens = oauth.fetch_access_token(config.get('xtwitter.access_token.url', "https://api.x.com/oauth/access_token"))

            session['access_token'] = oauth_tokens["oauth_token"]
            session['access_token_secret'] = oauth_tokens["oauth_token_secret"]
            session.save()

        elif config.get('xtwitter.oauth.type', 'oauth1').lower() == 'oauth2':
            oauth = OAuth2Session(
                client_id=config.get('xtwitter.client_id', ''),
                redirect_uri=url('/xauthorized', qualified=True),
                state=session['xoauth2_state']
            )

            if not session.has_key('xoauth2_challenge'):
                flash(_(u"I cannot find the data needed to validate "
                        u"the authorization challenge in the session. "
                        u"Maybe you are using a light version of "
                        u"the browser that cannot maintain a session "
                        u"or you have disabled the saving of cookies. "
                        u"Try to switch to a full-fledged browser or "
                        u"turn on the saving of cookies."), 'warning')
                redirect('/')

            try:
                oauth2_token = oauth.fetch_token(
                    token_url=config.get('xtwitter.oauth2_token.url', 'https://api.x.com/2/oauth2/token'),
                    client_id=config.get('xtwitter.client_id', ''),
                    client_secret=config.get('xtwitter.client_secret', ''),
                    code=kw.get('code', None),
                    code_verifier=session.get('xoauth2_challenge', '')
                )
            except:
                log.error(u"Can't fetch access token")
                flash(_(u"Can't fetch access token"), 'error')
                redirect('/')

            session['xoauth2_token'] = oauth2_token
            session.save()

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
        if config.get('xtwitter.oauth.type', 'oauth1').lower() == 'oauth1':
            del(session['resource_owner_key'])
            del(session['resource_owner_secret'])
            session.save()

        xuser = DBSession.query(model.XTwitter).filter(model.XTwitter.xid == session['me_on_xtwitter']['data']['id']).first()
        if xuser:
            xuser.user_name = session['me_on_xtwitter']['data']['username']
            xuser.display_name = session['me_on_xtwitter']['data']['name']
            xuser.user_info = json.dumps(session['me_on_xtwitter'])
            if request.identity:
                xuser.user = request.identity['user']
        else:
            xuser = model.XTwitter(
                xid=session['me_on_xtwitter']['data']['id'],
                user_name=session['me_on_xtwitter']['data']['username'],
                display_name=session['me_on_xtwitter']['data']['name'],
                user_info=json.dumps(session['me_on_xtwitter'])
            )
            if request.identity:
                xuser.user = request.identity['user']
            DBSession.add(xuser)
        DBSession.flush()

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
        flash(_("Successfully detached from X/Twitter, the access token has been discarded"))
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

        game_result = DBSession.query(model.GameResult, model.XTwitter).join(model.XTwitter, model.XTwitter.uid == model.GameResult.xtwitter_uid)
        game_result = game_result.filter(
            model.GameResult.game_no == parsed_vals['game_no'],
            model.XTwitter.xid == kw.get('xtwitter_uid', None)
        ).first()

        if game_result:
            flash(_(u"This game result is already in database"), 'warning')
            redirect('/')

        xuser = DBSession.query(model.XTwitter).filter(model.XTwitter.xid == kw.get('xtwitter_uid')).first()
        if not xuser:
            flash(_(u"X/Twitter user not found"), 'warning')
            redirect('/')

        game_result = model.GameResult(
            xtwitter=xuser,
            game_no=parsed_vals['game_no'],
            game_time=timedelta(seconds=parsed_vals['time']) if parsed_vals['time'] else None,
            game_rows=parsed_vals['step'],
            wednesday_challenge=kw.get('wednesday_challenge', None) if parsed_vals['game_no'] % 7 == 5 else None,
            comment=kw.get('comment', None) if kw.get('comment', None) else None,
            game_result_time=timedelta(seconds=parsed_vals['time'] + (parsed_vals['step'] - 1) * 12) if parsed_vals['time'] and parsed_vals['step'] else None,
            game_raw_data=kw.get('game_result', None)
        )

        DBSession.add(game_result)

        try:
            DBSession.flush()
        except Exception as e:
            flash(_(u"Something went wrong! Can't save game result to database, so it isn't sent to legacy website too!"), 'error')
            redirect('/')

        # Send data to legacy form (temporary function)
        viewform_url = "https://docs.google.com/forms/d/e/1FAIpQLSdHcMlAmXKOODsG0hZCc687_8oVZpFbv_GJXfA5P9aHn2IJgg/viewform"
        formaction_url = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdHcMlAmXKOODsG0hZCc687_8oVZpFbv_GJXfA5P9aHn2IJgg/formResponse"

        data = {
            "entry.1414922346": kw.get('game_result', '').replace('\n', ' '),
            "entry.125941353": kw.get('comment', ''),
            "entry.1818535534.other_option_response": kw.get('xtwitter_username', ''),
            "entry.1818535534": "__other_option__"
        }
        if kw.get('wednesday_challenge', False):
            data["entry.2012937700"] = "✅"

        rsess = requests.Session()
        rsess.get(viewform_url)
        r = rsess.post(formaction_url, data=data)

        if r.ok:
            flash(l_(u"Your result has been successfully saved to database and sent to the original website"))
        else:
            flash(l_(u"Your result has been successfully saved to database, but an error occurred while submitting the result from the form to legacy website. Let us know it!"), 'warning')

        rsess.close()

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
