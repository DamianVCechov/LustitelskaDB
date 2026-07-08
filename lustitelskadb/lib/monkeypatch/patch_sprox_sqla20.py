'''
Created on 8. 7. 2026

@author: jarda
'''

import sqlalchemy

def patch_sprox_sqla20():
    if sqlalchemy.__version__.startswith('2.'):
        from sqlalchemy import Table, MetaData
        from sqlalchemy.orm import DeclarativeMeta

        if not hasattr(Table, 'bind'):
            @property
            def table_bind_compat(self):
                return getattr(self.metadata, 'bind', None)
            Table.bind = table_bind_compat

        if not hasattr(MetaData, 'bind'):
            @property
            def metadata_bind_compat(self):
                return getattr(self, '_bind', None)
            @metadata_bind_compat.setter
            def metadata_bind_compat(self, value):
                self._bind = value
            MetaData.bind = metadata_bind_compat
