# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in LustitelskaDB.

This file complements development/deployment.ini.

"""
from tg import FullStackApplicationConfigurator, milestones
from tgext.pluggable import plug, replace_template

import lustitelskadb
from lustitelskadb import model, lib

base_config = FullStackApplicationConfigurator()

# General configuration
base_config.update_blueprint({
    # True to prevent dispatcher from striping extensions
    # For example /socket.io would be served by "socket_io"
    # method instead of "socket".
    'disable_request_extensions': False,

    # Set None to disable escaping punctuation characters to "_"
    # when dispatching methods.
    # Set to a function to provide custom escaping.
    'dispatch_path_translator': True,

    'package': lustitelskadb,
})

# ToscaWidgets configuration
base_config.update_blueprint({
    'tw2.enabled': True,
})

# Rendering Engines Configuration
rendering_config = {
    'renderers': ['json'],  # Enable json in expose
    'default_renderer': 'kajiki',
}
rendering_config['renderers'].append('kajiki')
# Change this in setup.py too for i18n to work.
rendering_config['templating.kajiki.strip_text'] = False
base_config.update_blueprint(rendering_config)

# Configure Sessions, store data as JSON to avoid pickle security issues
base_config.update_blueprint({
    'session.enabled': True,
    'session.data_serializer': 'json',
})

# Configure the base SQLALchemy Setup
base_config.update_blueprint({
    'use_sqlalchemy': True,
    'model': lustitelskadb.model,
    'DBSession': lustitelskadb.model.DBSession,
})
# This tells to TurboGears how to retrieve the data for your user
from tg.configuration.auth import TGAuthMetadata


class ApplicationAuthMetadata(TGAuthMetadata):

    def __init__(self, dbsession, user_class):
        self.dbsession = dbsession
        self.user_class = user_class

    def authenticate(self, environ, identity):
        login = identity['login']
        user = self.dbsession.query(self.user_class).filter_by(
            user_name=login
        ).first()

        if not user:
            login = None
        elif not user.validate_password(identity['password']):
            login = None

        if login is None:
            try:
                from urllib.parse import parse_qs, urlencode
            except ImportError:
                from urlparse import parse_qs
                from urllib import urlencode
            from tg.exceptions import HTTPFound

            params = parse_qs(environ['QUERY_STRING'])
            params.pop('password', None)  # Remove password in case it was there
            if user is None:
                params['failure'] = 'user-not-found'
            else:
                params['login'] = identity['login']
                params['failure'] = 'invalid-password'

            # When authentication fails send user to login page.
            environ['repoze.who.application'] = HTTPFound(
                location=environ['SCRIPT_NAME'] + '?'.join(('/login', urlencode(params, True)))
            )

        return login

    def get_user(self, identity, userid):
        return self.dbsession.query(self.user_class).filter_by(
            user_name=userid
        ).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]


# Configure the authentication backend
base_config.update_blueprint({
    'auth_backend': 'sqlalchemy',

    # YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
    'sa_auth.cookie_secret': "41c16350-55ec-4ba4-a624-f3cab07a57f8",
    'sa_auth.authmetadata': ApplicationAuthMetadata(model.DBSession, model.User),

    # You may optionally define a page where you want users
    # to be redirected to on login:
    'sa_auth.post_login_url': '/post_login',

    # You may optionally define a page where you want users
    # to be redirected to on logout:
    'sa_auth.post_logout_url': '/post_logout',

    # In case ApplicationAuthMetadata didn't find the user discard the whole identity.
    # This might happen if logged-in users are deleted.
    'identity.allow_missing_user': False,

    # override this if you would like to provide a different who plugin for
    # managing login and logout of your application
    'sa_auth.form_plugin': None,

    # You can use a different repoze.who Authenticator if you want to
    # change the way users can login
    # 'sa_auth.authenticators': [('myauth', SomeAuthenticator()],

    # You can add more repoze.who metadata providers to fetch
    # user metadata.
    # Remember to set 'sa_auth.authmetadata' to None
    # to disable authmetadata and use only your own metadata providers
    # 'sa_auth.mdproviders': [('myprovider', SomeMDProvider()],
})

try:
    # Enable DebugBar if available, install tgext.debugbar to turn it on
    from tgext.debugbar import enable_debugbar
    enable_debugbar(base_config)
except ImportError:
    pass

try:
    # Enable TGapp Permissions if available, install tgapp-permissions to turn it on
    plug(base_config, 'tgapppermissions')
except ImportError:
    pass

try:
    # Enable TGExt Mailer if available, install tgext.mailer to turn it on
    plug(base_config, 'tgext.mailer')
except ImportError:
    pass

try:
    # Enable User Registration if available, install tgapp-registration to turn it on
    plug(base_config, 'registration')
    base_config.update_blueprint({
        '_pluggable_registration_config': {
            'form': 'lustitelskadb.lib.forms.UserRegistration'
        }
    })
    replace_template(base_config, 'registration.templates.register', 'lustitelskadb.templates.registration.register')
    replace_template(base_config, 'registration.templates.complete', 'lustitelskadb.templates.registration.complete')
except ImportError:
    pass

try:
    # Enable Reset Password if available, install tgapp-resetpassword to turn it on
    plug(base_config, 'resetpassword')
    base_config.update_blueprint({
        '_pluggable_resetpassword_config': {
            'reset_password_form': 'lustitelskadb.lib.forms.ResetPasswordForm'
        }
    })
    replace_template(base_config, 'resetpassword.templates.index', 'lustitelskadb.templates.resetpassword.index')
    replace_template(base_config, 'resetpassword.templates.change_password', 'lustitelskadb.templates.resetpassword.change_password')
except ImportError:
    pass

try:
    # Enable User Profile if available, install tgapp-userprofile to turn it on
    plug(base_config, 'userprofile')
except ImportError:
    pass

def replace_profile_form_layout():
    from axf.bootstrap import BootstrapFormLayout
    from userprofile.lib import UserForm
    from resetpassword.lib.forms import NewPasswordForm

    UserForm.child = BootstrapFormLayout(children=UserForm.child.children)
    UserForm.submit.css_class = 'btn btn-outline-secondary mt-3'

    NewPasswordForm.child = BootstrapFormLayout(children=NewPasswordForm.child.children)
    NewPasswordForm.submit.css_class = 'btn btn-outline-secondary mt-3'

milestones.config_ready.register(replace_profile_form_layout)
