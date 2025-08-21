# -*- coding: utf-8 -*-
"""Clan model module."""
from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref

from lustitelskadb.model import DeclarativeBase, metadata, DBSession

__all__ = ('Clan', 'ClanMember')


class Clan(DeclarativeBase):
    __tablename__ = 'clan'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)

    name = Column(Unicode(64), nullable=False, default='')
    symbol = Column(Unicode(16), nullable=False, default='')


class ClanMember(DeclarativeBase):
    __tablename__ = 'clan_members'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)

    clan_id = Column(Integer, ForeignKey(Clan.uid), index=True)
    clan = relationship(Clan, backref=backref('members'))

    user_id = Column(Integer, ForeignKey('tg_user.user_id'), index=True)
    user = relationship('User', uselist=False,
                        backref=backref('clan_member',
                                        cascade='all, delete-orphan',
                                        uselist=False))
