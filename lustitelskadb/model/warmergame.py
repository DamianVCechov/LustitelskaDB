# -*- coding: utf-8 -*-
'''
Warmer Game model module.

Created on 8. 7. 2026

@author: jarda
'''

from sqlalchemy import Table, ForeignKey, Column, func
from sqlalchemy.types import Integer, SmallInteger, Unicode, Date, DateTime, UnicodeText
from sqlalchemy.orm import relationship, backref

from lustitelskadb.model import DeclarativeBase, metadata, DBSession

__all__ = ['WarmerGame', 'WarmerGameResult']


class WarmerGame(DeclarativeBase):
    """Warmer Games data table."""

    __tablename__ = 'warmer_games'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    game_date = Column(Date, nullable=False, unique=True, default=func.now(), server_default=func.now())
    word = Column(Unicode(32), nullable=True, index=True)

    # Meta data
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())


class WarmerGameResult(DeclarativeBase):
    """Warmer Games results table."""

    __tablename__ = 'warmer_games_results'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User', backref=backref('warmer_results'))
    game_date = Column(Date, nullable=False, index=True, default=func.now(), server_default=func.now())
    game_guesses = Column(SmallInteger, nullable=True, index=True)
    comment = Column(UnicodeText, nullable=True)

    # Meta data
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())
