# -*- coding: utf-8 -*-
"""SNS model module."""
from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, UnicodeText
from sqlalchemy.orm import relationship, backref

from lustitelskadb.model import DeclarativeBase, metadata, DBSession

__all__ = ['XTwitter', 'Atmosphere']


class XTwitter(DeclarativeBase):
    __tablename__ = 'xtwitter'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    xid = Column(String(20), unique=True, nullable=False, default='')
    user_name = Column(Unicode(15), unique=True, nullable=False, default=u'')
    display_name = Column(Unicode(50), unique=False, nullable=False, default=u'')
    user_info = Column(UnicodeText)

    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User',
                        backref=backref('xuser', uselist=False,
                                        cascade='all, delete-orphan'))

class Atmosphere(DeclarativeBase):
    __tablename__ = 'atmosphere'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    did = Column(String(300), unique=True, nullable=False, default='', server_default='')
    user_name = Column(String(255), unique=True, nullable=False, default='', server_default='')
    display_name = Column(Unicode(64), nullable=True)
    user_info = Column(UnicodeText, nullable=True)

    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User',
                        backref=backref('atuser', uselist=False,
                                        cascade='all, delete-orphan'))
