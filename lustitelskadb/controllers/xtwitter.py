# -*- coding: utf-8 -*-
"""X/Twitter controller module"""

from tg import expose, redirect, validate, flash, url, require, tmpl_context, config, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
# from tg import predicates
from tg.predicates import has_any_permission

from lustitelskadb.lib.base import BaseController
# from lustitelskadb.model import DBSession

from requests_oauthlib import OAuth1Session
import tweepy

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
            tmpl_context.form.value = {}
            tmpl_context.form.value['text'] = kw.get('text', '')

        return dict(page='admin-xtwitter-index')

    def upload_media(files):
        """Upload media to X/Twitter"""
        text = str(post)
        media_id = re.search("media_id=(.+?),", text).group(1)
        payload = {"media": {"media_ids": ["{}".format(media_id)]}}
        os.remove("catpic.jpg")
        return payload

    @expose()
    @validate(form=appforms.XTwitterPostForm(), error_handler=index)
    @require(has_any_permission('manage', 'xtwitter', msg=l_('Only for users with appropriate permissions')))
    def create_post(self, **kw):
        """Create post on X/Twitter"""
        oauth = OAuth1Session(
            config.get('xtwitter.consumer_key', ''),
            client_secret=config.get('xtwitter.consumer_secret', ''),
            resource_owner_key=config.get('xtwitter.access_key', ''),
            resource_owner_secret=config.get('xtwitter.access_secret', '')
        )

        media_ids = []
        if kw.get('medialist', []):
            tweepy_auth = tweepy.OAuth1UserHandler(
                config.get('xtwitter.consumer_key', ''),
                config.get('xtwitter.consumer_secret', ''),
                config.get('xtwitter.access_key', ''),
                config.get('xtwitter.access_secret', '')
            )
            tweepy_api = tweepy.API(tweepy_auth)

            for media in kw.get('medialist', [])[:4]:
                post = tweepy_api.media_upload(filename=media['media'].filename, file=media['media'].file)
                media_ids.append(post.media_id_string)

        payload = {
            'text': kw.get('text', '')
        }
        if media_ids:
            payload['media'] = {
                'media_ids': media_ids
            }

        response = oauth.post(
            "https://api.x.com/2/tweets",
            json=payload
        )

        oauth.close()

        if response.ok:
            flash(_(u"Post successfully sent to X/Twitter."))
            return redirect('/admin/xtwitter')
        else:
            flash(_(u"Something went wrong, during sending post to X/Twitter. Error Code: {}").format(response.status_code), 'error')
            return redirect('/admin/xtwitter', params=kw)
