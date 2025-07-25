# -*- coding: utf-8 -*-

#  Quickstarted Options:
#
#  sqlalchemy: True
#  auth:       sqlalchemy
#  mako:       False
#
#

# This is just a work-around for a Python2.7 issue causing
# interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = [
    'WebTest >= 1.2.3',
    'nose',
    'coverage',
    'gearbox'
]

full_extras = [
    'ujson'
]

install_requires = [
    "TurboGears2 >= 2.4.0",
    "Beaker >= 1.8.0",
    "Kajiki >= 0.6.3",
    "zope.sqlalchemy >= 1.1",
    "sqlalchemy",
    "alembic",
    "repoze.who",
    "tw2.forms",
    "tw2.dynforms",
    "tgext.admin >= 0.6.1",
    "WebHelpers2",
    "requests",
    "requests_oauthlib",
    "tweepy",
    "pathlib; python_version < '3.4'",
    # "csv", # Temporary disabled
    # "magic" # Temporary disabled
]

if py_version != (3, 2):
    # Babel not available on 3.2
    install_requires.append("Babel")

setup(
    name='LustitelskaDB',
    version='1.5.0',
    description='Hobby web application for statistics czech Wordle game named HadejSlova',
    author='ByCzech, DamianVCechov',
    author_email='byczech@gmail.com, lustitele@gmail.com',
    url='http://lusteni.nemachybu.cz',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    extras_require={
        'testing': testpkgs,
        'full': full_extras
    },
    package_data={'lustitelskadb': [
        'i18n/*/LC_MESSAGES/*.mo',
        'templates/*/*',
        'public/*/*'
    ]},
    message_extractors={'lustitelskadb': [
        ('**.py', 'python', None),
        ('templates/**.xhtml', 'kajiki', {'strip_text': False, 'extract_python': True}),
        ('public/**', 'ignore', None)
    ]},
    entry_points={
        'paste.app_factory': [
            'main = lustitelskadb.config.application:make_app'
        ],
        'gearbox.plugins': [
            'turbogears-devtools = tg.devtools'
        ]
    },
    zip_safe=False
)
