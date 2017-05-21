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
    name = Column(Unicode(255), nullable=False,default="")
    start = Column(Unicode(255), nullable=False,default="12:00 AM")
    end = Column(Unicode(255), nullable=False,default="")
    category = Column(Unicode(255), nullable=False,default="")
    description = Column(Unicode(255), nullable=False,default="")
    location = Column(Unicode(255), nullable=False,default="")
    extlink = Column(Unicode(255), nullable=False,default="")
    tickets = Column(Unicode(255), nullable=False,default="")
    pri = Column(Unicode(255), nullable=False,default="")
    recipe_num = Column(Unicode(255), nullable=False,default="")
    band_name = Column(Unicode(255), nullable=False,default="")
    series = Column(Unicode(255), nullable=False,default="")
    source = Column(Unicode(255), nullable=False,default="")
    image = Column(Unicode(255), nullable=False,default="")
    keywords = Column(Unicode(255), nullable=False,default="")
    category2 = Column(Unicode(255), nullable=False,default="")
    marketing = Column(Unicode(255), nullable=False,default="")
    color = Column(Unicode(255), nullable=False,default="")
    
    aero_email = Column(Unicode(255), nullable=False,default="")
    notes = Column(Unicode(1023), nullable=False,default="")
    partner_name = Column(Unicode(255), nullable=False,default="")
    partner_email = Column(Unicode(255), nullable=False,default="")
    payment = Column(Unicode(255), nullable=False,default="")
    pending = Column(Unicode(255), nullable=False,default="")
    private = Column(Unicode(255), nullable=False,default="")


class Partner(Base):
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    #events = relationship('Event')

import json, os, pprint

    
def main():  
    from sqlalchemy import create_engine
    from settings import DB_URI
    from db import nonflask_session as session
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    data_dir="_data"



    events = []
    
    with open(os.path.join(data_dir,"events1.json")) as f:
            event_data = json.load(f)["all_events"]
    for e in event_data:
        e_cleaned = dict(**e)
        e_cleaned["date"] = dateparser.parse(e["date"])
        events.append(Event(**e_cleaned))

    
    with open(os.path.join(data_dir,"past_events1.json")) as f:
            event_data = json.load(f)
    for e in event_data:
        e_cleaned = dict(**e)
        e_cleaned["date"] = dateparser.parse(e["date"])
        events.append(Event(**e_cleaned))


        

    session.add_all(events)
    session.commit()



if __name__ == "__main__":
    main()

