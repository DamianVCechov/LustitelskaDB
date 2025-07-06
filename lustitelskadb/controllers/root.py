# -*- coding: utf-8 -*-
"""Main Controller"""

import logging
log = logging.getLogger(__name__)

from tg import expose, flash, require, url, lurl, abort, response
from tg import request, redirect, tmpl_context, validate, session, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from tg.decorators import paginate
from tg.support.converters import asbool

from lustitelskadb.lib.helpers import wednesday_challenge_words_window

from lustitelskadb import model
from lustitelskadb.model import DBSession

from sqlalchemy.sql.expression import func

import tw2.core as twc

import requests
from requests_oauthlib import OAuth1Session, OAuth2Session

import os
import random
import string
from datetime import datetime, timedelta

# from base64 import b64encode
# from magic import Magic

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
from lustitelskadb.lib.injects import closing_deadline_jssrc, emojipicker_init_jssrc
from lustitelskadb.lib.utils import *

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
    def _default(self, game=None, *args, **kw):
        """Handle the front-page."""
        comments = DBSession.query(model.GameResult).filter(model.GameResult.comment != None, model.GameResult.comment != '').order_by(func.random()).limit(100).all()

        game_nums = DBSession.query(model.GameResult.game_no)
        if game and game.isdigit():
            game_nums = game_nums.filter(model.GameResult.game_no <= game)
        elif game and not game.isdigit():
            abort(404)
        game_nums = game_nums.order_by(model.GameResult.game_no.desc()).distinct().limit(2).all()
        if not game_nums:
            abort(404)

        latest_game = DBSession.query(model.GameResult.game_no).order_by(model.GameResult.game_no.desc()).first()
        oldest_game = DBSession.query(model.GameResult.game_no).order_by(model.GameResult.game_no).first()

        games = []
        for lg in game_nums:
            game = DBSession.query(model.GameResult).filter(model.GameResult.game_no == lg.game_no)
            if lg.game_no % 7 == 5:
                game = game.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.wednesday_challenge.desc(), model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())
            else:
                game = game.order_by(model.GameResult.game_rows == None, model.GameResult.game_result_time == None, model.GameResult.game_result_time, model.GameResult.game_rows, model.GameResult.game_time.desc())
            games.append(game.all())

        game_in_progress = today_game_no()

        popover_titles_jssrc = twc.JSSource(src='''
            $(() => {
                $('[title]').popover({ trigger: "hover", placement: "top" });
            });
        ''')

        closing_deadline_jssrc.inject()
        popover_titles_jssrc.inject()

        return dict(page='index', comments=comments, game_nums=game_nums, games=games, latest_game=latest_game, oldest_game=oldest_game, game_in_progress=game_in_progress)

    @expose('json')
    def get_daily_wallpaper(self, **kw):
        """Get Daily Wallpaper"""
        # mime = Magic(mime=True)

        cache_path = os.path.join(config.get('cache_dir'), 'cache', 'daily_wallpaper')
        if not os.path.exists('cache_path'):
            try:
                os.makedirs(cache_path)
            except:
                pass

        if os.path.isfile(os.path.join(cache_path, 'wallpaper.json')):
            with open(os.path.join(cache_path, 'wallpaper.json'), "r") as f:
                data = json.load(f)
        else:
            data = None

        if data and datetime.now() >= datetime.strptime(data.get('images', [{}])[0].get('fullstartdate'), "%Y%m%d%H%M"):
            reload_wallpaper = True
        else:
            reload_wallpaper = False

        if not data or reload_wallpaper:
            sess = requests.Session()
            r = sess.get('https://www.bing.com/hpimagearchive.aspx', params={'format': 'js', 'idx': 0, 'n': 1})
            if r.ok:
                if r.apparent_encoding:
                    data = r.json()
                    reload_wallpaper = True
                    with open(os.path.join(cache_path, 'wallpaper.json'), "w") as f:
                        json.dump(data, f)

        # mime_type = ''
        # img = ''
        if data and reload_wallpaper:
            img_url = data.get('images', [{}])[0].get('url', '')
            if img_url:
                r_img = sess.get("https://bing.com{}".format(img_url))
                if r_img.ok:
                    # mime_type = mime.from_buffer(r_img.content)
                    # img = b64encode(r_img.content)
                    with open(os.path.join(cache_path, 'wallpaper_image'), "wb") as f:
                        f.write(r_img.content)

        if data:
            return dict(url=url('/daily_wallpaper', params={'v': data.get('images', [{}])[0].get('fullstartdate')}))
        else:
            return dict(url='')
        return dict(url="data:{};base64,{}".format(mime_type, '' if not img else img.decode('ascii')))

    @expose(content_type="image/jpeg")
    def daily_wallpaper(self, **kw):
        """Return cached wallpaper."""
        cache_path = os.path.join(config.get('cache_dir'), 'cache', 'daily_wallpaper')
        if not os.path.exists('cache_path'):
            try:
                os.makedirs(cache_path)
            except:
                pass

        response.headerlist.append(('Content-Disposition', 'inline; filename=daily_wallpaper.jpg'.format()))

        if os.path.isfile(os.path.join(cache_path, 'wallpaper_image')):
            with open(os.path.join(cache_path, 'wallpaper_image'), "rb") as f:
                return f.read()
        else:
            return None

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

        user_game_stats = DBSession.query(
            func.avg(func.ifnull(model.GameResult.game_rows, 7)).label('avg_rows'),
            func.avg(model.GameResult.game_rows).label('avg_solved_rows'),
            func.avg(model.GameResult.game_time).label('avg_time'),
            func.avg(model.GameResult.game_result_time).label('avg_result_time'),
            func.avg(model.GameResult.game_rank).label('avg_rank'),
            func.avg(model.GameResult.game_points).label('avg_points'),
            func.sum(model.GameResult.game_points).label('sum_points')
        ).filter(model.GameResult.user_id == gameresult.user_id, model.GameResult.game_no <= gameresult.game_no, model.GameResult.game_result_time != None).first()

        user_game_rank_stats = DBSession.query(
            model.GameResult.game_rank,
            func.count(model.GameResult.game_rank)
        ).filter(model.GameResult.user_id == gameresult.user_id, model.GameResult.game_no <= gameresult.game_no).group_by(model.GameResult.game_rank).order_by(model.GameResult.game_points.desc(), model.GameResult.game_rank).all()

        played_games = DBSession.query(model.GameResult).filter(model.GameResult.user_id == gameresult.user_id, model.GameResult.game_no <= gameresult.game_no).count()
        solved_games = DBSession.query(model.GameResult).filter(model.GameResult.user_id == gameresult.user_id, model.GameResult.game_no <= gameresult.game_no, model.GameResult.game_rows != None).count()
        obtained_lanterns = DBSession.query(model.GameResult).filter(model.GameResult.user_id == gameresult.user_id, model.GameResult.game_no <= gameresult.game_no, model.GameResult.game_rows > 1, model.GameResult.game_time != None, model.GameResult.game_points == 0).count()

        return dict(page="detail", gameresult=gameresult, user_game_stats=user_game_stats, played_games=played_games, solved_games=solved_games, obtained_lanterns=obtained_lanterns, user_game_rank_stats=user_game_rank_stats)

    @expose()
    def xauthorize(self, **kw):
        """Authorize via X/Twitter."""
        redirect('/xerror')  # Temporarily hardcoded redirect, becase of non functional X/Twitter API

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
    @require(predicates.not_anonymous(msg=l_('Only for users with appropriate permissions')))
    def newresult(self, **kw):
        """Handle page with registering new user game result."""
        tmpl_context.form = appforms.ResultForm()

        if today_game_no() % 7 == 5:
            tmpl_context.form.child.children.wednesday_challenge.container_attrs = {
                'style': 'color: var(--bs-danger);'
            }
            tmpl_context.form.child.children.wednesday_challenge.required = True

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

        return dict(page='newresult')

    @expose()
    @require(predicates.not_anonymous(msg=l_('Only for users with appropriate permissions')))
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

        # Unicorns has no time in result
        if parsed_vals['step'] == 1 and parsed_vals['time'] == None:
            parsed_vals['time'] == 0

        if parsed_vals['game_no'] != today_game_no():
            flash(_("This result can't be saved, because isn't for actually ongoing game!"), 'error')
            redirect('/')

        game_result = DBSession.query(model.GameResult)
        game_result = game_result.filter(
            model.GameResult.game_no == parsed_vals['game_no'],
            model.GameResult.user == request.identity['user']
        ).first()

        if game_result:
            flash(_(u"This game result is already in database"), 'warning')
            redirect('/')

        game_result = model.GameResult(
            user=request.identity['user'],
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
        except Exception as e:
            flash(_(u"Something went wrong! Can't save game result to database, so it isn't sent to legacy website too!"), 'error')
            redirect('/')

        assemble_game_scoresheet(parsed_vals['game_no'])

        flash(l_(u"Your result has been successfully saved to database"))
        return redirect('/')

    @expose('lustitelskadb.templates.wednesday_challenge')
    def wednesday_challenge(self, **kw):
        """Handle page with words for next comming Wednesday challenge."""
        tmpl_context.form = appforms.WednesdayChallengeWordsForm()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value
        else:
            tmpl_context.form.value = dict()

        wc_words_form_open = False
        wc_words = DBSession.query(model.WednesdayChallengeWord).filter(model.WednesdayChallengeWord.game_no >= today_game_no()).first()
        if wc_words:
            next_wc = game_no_start_date(wc_words.game_no)
        else:
            next_wc = None
            if predicates.has_permission('wednesday_master') and wednesday_challenge_words_window():
                wc_words_form_open = True
            elif predicates.not_anonymous() and wednesday_challenge_words_window():
                user_result_in_monday_game = DBSession.query(model.GameResult, model.User).join(model.User, model.User.user_id == model.GameResult.user_id).filter(model.GameResult.game_no == today_game_no() - 1, model.User.user_id == request.identity['user'].user_id).first()
                last_monday_game_rank = DBSession.query(model.GameResult).filter(model.GameResult.game_no == today_game_no() - 1).order_by(model.GameResult.game_rank.desc(), model.GameResult.uid.desc()).first()
                if user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank != user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=user_rank_hours_offset.get(user_result_in_monday_game[0].game_rank, 24)) <= datetime.now():
                    wc_words_form_open = True
                elif user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank > 0 and last_monday_game_rank.game_rank != user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=23) <= datetime.now():
                    wc_words_form_open = True
                elif user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank == user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=23, minutes=59) <= datetime.now():
                    wc_words_form_open = True

        emoji_picker_jslnk = twc.JSLink(
            location="bodybottom",
            type="module",
            link="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js",
            template='kajiki:lustitelskadb.templates.tw2.core.jslink'
        )

        emoji_picker_jslnk.inject()
        emojipicker_init_jssrc.inject()

        return dict(page="wednesday_challenge", wc_words=wc_words, next_wc=next_wc, wc_words_form_open=wc_words_form_open)

    @expose()
    @require(predicates.not_anonymous(msg=l_('Only for users with appropriate permissions')))
    @validate(form=appforms.WednesdayChallengeWordsForm(), error_handler=wednesday_challenge)
    def save_wednesday_challenge_words(self, **kw):
        """Save Wednesday challenge words."""
        wc_words_form_open = False
        wc_words = DBSession.query(model.WednesdayChallengeWord).filter(model.WednesdayChallengeWord.game_no >= today_game_no()).first()

        if wc_words:
            flash(l_(u"Words for next Wednesday challenge is already in database! Try it again in next week!"))
            return redirect('/')

        if predicates.has_permission('manage') and wednesday_challenge_words_window():
            wc_words_form_open = True
        elif predicates.not_anonymous() and wednesday_challenge_words_window():
            user_result_in_monday_game = DBSession.query(model.GameResult, model.User).join(model.User, model.User.user_id == model.GameResult.user_id).filter(model.GameResult.game_no == today_game_no() - 1, model.User.user_id == request.identity['user'].user_id).first()
            last_monday_game_rank = DBSession.query(model.GameResult).filter(model.GameResult.game_no == today_game_no() - 1).order_by(model.GameResult.game_rank.desc(), model.GameResult.uid.desc()).first()
            if user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank != user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=user_rank_hours_offset.get(user_result_in_monday_game[0].game_rank, 24)) <= datetime.now():
                wc_words_form_open = True
            elif user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank > 0 and last_monday_game_rank.game_rank != user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=23) <= datetime.now():
                wc_words_form_open = True
            elif user_result_in_monday_game and last_monday_game_rank and last_monday_game_rank.game_rank == user_result_in_monday_game[0].game_rank and game_no_start_date(today_game_no()) + timedelta(hours=23, minutes=59) <= datetime.now():
                wc_words_form_open = True

        if not wc_words_form_open:
            flash(l_("You can't sent words for Wednesday challenge"), 'error')
            return redirect('/')

        wc_words = model.WednesdayChallengeWord(
            game_no=today_game_no() + 1,
            first_word=kw.get('first_word', '-----').upper(),
            second_word=kw.get('second_word', '-----').upper(),
            third_word=kw.get('third_word', '-----').upper(),
            comment=kw.get('comment', None),
            user=request.identity['user']
        )

        DBSession.add(wc_words)
        DBSession.flush()

        flash(l_("Words has been successfully saved to database for next Wednesday challenge! Thanx!"))

        return redirect('/')

    @expose('lustitelskadb.templates.rankings')
    def rankings(self, period=None, *kw):
        """Handle game results rankings."""
        if period not in ('year', 'month', 'week', '3day'):
            period = None

        all_games = DBSession.query(model.GameResult.game_no).filter(model.GameResult.game_no < today_game_no())

        ranking = DBSession.query(
            func.count(model.GameResult.game_no).label('played_games'),
            func.sum(model.GameResult.game_points).label('points_sum'),
            func.avg(model.GameResult.game_points).label('points_avg'),
            model.User.display_name.label('display_name')
        ).join(model.User).filter(model.GameResult.game_no < today_game_no())

        if period == "year":
            ranking = ranking.filter(model.GameResult.game_no >= today_game_no() - 365)
            all_games = all_games.filter(model.GameResult.game_no >= today_game_no() - 365)
        elif period == "month":
            ranking = ranking.filter(model.GameResult.game_no >= today_game_no() - 28)
            all_games = all_games.filter(model.GameResult.game_no >= today_game_no() - 28)
        elif period == "week":
            ranking = ranking.filter(model.GameResult.game_no >= today_game_no() - 7)
            all_games = all_games.filter(model.GameResult.game_no >= today_game_no() - 7)
        elif period == "3day":
            ranking = ranking.filter(model.GameResult.game_no >= today_game_no() - 3)
            all_games = all_games.filter(model.GameResult.game_no >= today_game_no() - 3)

        all_games = all_games.distinct().count()
        ranking = ranking.group_by(model.GameResult.user_id).order_by(func.sum(model.GameResult.game_points).desc()).all()

        popover_titles_jssrc = twc.JSSource(src='''
            $(() => {
                $('[title]').popover({ trigger: "hover", placement: "top" });
            });
        ''')

        popover_titles_jssrc.inject()

        return dict(page="rankings", all_games=all_games, ranking=ranking)

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
