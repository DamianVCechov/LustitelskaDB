# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""LibriCiphers model module."""
from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime, LargeBinary
from sqlalchemy.orm import relationship, backref

from lustitelskadb.model import DeclarativeBase, metadata, DBSession

__all__ = ['LibriCipher']


class LibriCipher(DeclarativeBase):
    """LibriCipher Quiz Game Table definition."""

    __tablename__ = 'libriciphers'
    __table_args__ = {
                      'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'
    }

    uid = Column(Integer, primary_key=True)

    part = Column(Integer, index=True, nullable=False, default=0)

    question = Column(Unicode(100), nullable=False, default="")

    description = Column(UnicodeText)

    answer = Column(UnicodeText)
