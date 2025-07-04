# -*- coding: utf-8 -*-
"""Game model module."""
from sqlalchemy import Table, ForeignKey, Column, func
from sqlalchemy.types import Integer, Unicode, DateTime, Time, UnicodeText, Boolean
from sqlalchemy.orm import relationship, backref

from lustitelskadb.model import DeclarativeBase, metadata, DBSession

__all__ = ['GameResult', 'WednesdayChallengeWord']


class GameResult(DeclarativeBase):
    """Games results table."""

    __tablename__ = 'games_results'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User', backref=backref('results'))
    game_no = Column(Integer, nullable=False, index=True, default=0)
    game_time = Column(Time, nullable=True, index=True)
    game_rows = Column(Integer, nullable=True, index=True)
    wednesday_challenge = Column(Boolean, nullable=True, index=True)
    comment = Column(UnicodeText, nullable=True)
    # Results
    game_result_time = Column(Time, nullable=True, index=True)
    game_points = Column(Integer, nullable=False, index=True, default=0)
    game_rank = Column(Integer, nullable=True, index=True)
    # Raw data
    game_raw_data = Column(UnicodeText(255), nullable=False, default='')
    # Meta data
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())


class WednesdayChallengeWord(DeclarativeBase):
    """Wednesday Challenge words."""

    __tablename__ = 'wednesday_challenge_words'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User', backref=backref('wednesday_challenges'))
    # Game no (modulo 7 need to be = 5)
    game_no = Column(Integer, nullable=False, index=True, default=0)
    # Words need to be 5 chars exactly
    first_word = Column(Unicode(5), nullable=False, index=True, default='')
    second_word = Column(Unicode(5), nullable=False, index=True, default='')
    third_word = Column(Unicode(5), nullable=False, index=True, default='')
    comment = Column(UnicodeText, nullable=True)
    # Meta data
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())
