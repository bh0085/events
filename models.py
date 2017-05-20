#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv

import sqlite3

from decimal import Decimal
from datetime import date, datetime, timedelta

from sqlalchemy.orm import relationship, backref, configure_mappers, synonym
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, Numeric, String, Unicode, Text, Date, DateTime, Time, Boolean, ForeignKey, UniqueConstraint, func

from sqlalchemy.engine import Engine
from sqlalchemy import event

Base = declarative_base()

# enforce foreign keys in sqlite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    name = Column(Unicode(255), nullable=False)


class Partner(Base):
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    #events = relationship('Event')

def main():  
    from sqlalchemy import create_engine
    from settings import DB_URI
    from db import nonflask_session as session
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    events = [
        Event(date=date.today(), name='test event'),
        Event(date=date.today()+timedelta(days=1), name='test event2'),
        Event(date=date.today()+timedelta(days=2), name='test event3'),
    ]
    session.add_all(events)
    session.commit()

if __name__ == "__main__":
    main()

