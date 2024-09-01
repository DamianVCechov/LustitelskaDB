# -*- coding: utf-8 -*-
"""Setup the LustitelskaDB application"""
from __future__ import print_function

from tg import config
from tgext.pluggable import plugged
import transaction

try:
    ModuleNotFoundError
except:
    ModuleNotFoundError = ImportError


def setup_schema(command, conf, vars):
    """Place any commands to setup lustitelskadb here"""
    # Load the models

    # <websetup.websetup.schema.before.model.import>
    from lustitelskadb import model
    # <websetup.websetup.schema.after.model.import>

    # <websetup.websetup.schema.before.metadata.create_all>
    print("Creating tables")
    model.metadata.create_all(bind=config['tg.app_globals'].sa_engine)
    # <websetup.websetup.schema.after.metadata.create_all>
    transaction.commit()

    print('Initializing Migrations')
    import alembic.config
    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option("script_location", "migration")
    alembic_cfg.set_main_option("sqlalchemy.url", config['sqlalchemy.url'])
    import alembic.command
    alembic.command.stamp(alembic_cfg, "head")

    import alembic.util
    for plugapp in plugged():
        try:
            __import__("{}.migration".format(plugapp))
            print('Setting migration stamp for', plugapp)
            alembic_cfg.set_main_option("script_location", "{}:migration".format(plugapp))
            alembic.command.stamp(alembic_cfg, "head")
        except (ImportError, ModuleNotFoundError, alembic.util.exc.CommandError):
            # quietly pass if plugapp hasn't migration enabled
            # print('No migration enabled')
            pass
    # <websetup.websetup.schema.after.alembic.command.stamp>

    transaction.commit()
