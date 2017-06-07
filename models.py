#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv

import sqlite3

from decimal import Decimal
from datetime import date, datetime, timedelta
import dateparser


from sqlalchemy.orm import relationship, backref, configure_mappers, synonym
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, Numeric, String, Unicode, Text, Date, DateTime, Time, Boolean, ForeignKey, UniqueConstraint, func

from sqlalchemy.engine import Engine
from sqlalchemy import event

from flask_sqlalchemy import SQLAlchemy
db2 = SQLAlchemy()


# enforce foreign keys in sqlite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()

class Event(db2.Model):
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
    recipe_num = Column(Unicode(255), nullable=False,default="")
    band_name = Column(Unicode(255), nullable=False,default="")
    series = Column(Unicode(255), nullable=False,default="")
    source = Column(Unicode(255), nullable=False,default="")
    image = Column(Unicode(255), nullable=False,default="")
    keywords = Column(Unicode(255), nullable=False,default="")
    category2 = Column(Unicode(255), nullable=False,default="")
    marketing = Column(Unicode(255), nullable=False,default="")

    created = Column(DateTime, nullable=False)
    updated= Column(DateTime, nullable=False)
    created_user= Column(Unicode(255), nullable=False,default="")
    updated_user= Column(Unicode(255), nullable=False,default="")

    notes = Column(Unicode(1023), nullable=False,default="")
    partner_name = Column(Unicode(255), nullable=False,default="")
    partner_email = Column(Unicode(255), nullable=False,default="")
    payment = Column(Unicode(255), nullable=False,default="")
    pending = Column(Boolean, nullable=False,default=False)
    private = Column(Boolean, nullable=False,default=False)
    deleted = Column(Boolean, nullable=False,default=False)

    offsite_address=Column(Unicode(255),nullable=False, default="")
    offsite_name=Column(Unicode(255),nullable=False, default="")
    series_name=Column(Unicode(255),nullable=False, default="")
    private_invoiceamount =Column(Unicode(255),nullable=False, default="")
    private_invoicepaid=Column(Boolean,nullable=False, default=False)
    private_numguests=Column(Unicode(255),nullable=False, default="")
    private_barminimum=Column(Unicode(255),nullable=False, default="")
    private_invoicenum=Column(Unicode(255),nullable=False, default="")
    private_eventtype=Column(Unicode(255),nullable=False, default="")

    @property
    def pri(self):
        if self.category == "offsite":
            return 11
        elif self.category == "day":
            return 9
        elif self.category =="closed":
            return 8
        elif self.category =="modified hours":
            return 8
        elif self.category =="chocolate":
            return 11
        else:
            return 10


        return 
        
class Partner(db2.Model):
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    #events = relationship('Event')

import json, os, pprint

    
def main():

    print "not running this function. it will destroy everything"
    return
    from sqlalchemy import create_engine
    from settings import DB_URI
    from db import nonflask_session as session
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    data_dir="_data"



    events = []
    
    with open("/home/dan/aeronaut-events/actual_all_events.json") as f:
            event_data = json.load(f)
    for e in event_data:
        e_cleaned = dict(**e)
        e_cleaned["date"] = dateparser.parse(e["date"])
        
        e_cleaned["updated"] = datetime.now()
        e_cleaned["created"] = datetime.now()
        e_cleaned["created_user"] = e["aero_email"].split("@")[0]
        e_cleaned["updated_user"] = e["aero_email"].split("@")[0]

        del e_cleaned["aero_email"]
        del e_cleaned["pri"]
        del e_cleaned["color"]
        
        events.append(Event(**e_cleaned))

 

   #
   #with open(os.path.join(data_dir,"past_events1.json")) as f:
   #        event_data = json.load(f)
   #for e in event_data:
   #    e_cleaned = dict(**e)
   #    e_cleaned["date"] = dateparser.parse(e["date"])
   #    current_time = datetime.utcnow()
   #    week_start = current_time - timedelta(days=current_time.weekday()+7)
   #    if e_cleaned["date"] < week_start:       
   #        events.append(Event(**e_cleaned))


        

    session.add_all(events)
    session.commit()



if __name__ == "__main__":
    pass
    ##main()

