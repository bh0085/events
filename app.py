#!/usr/bin/env python

import os
import json
from collections import OrderedDict
import aniso8601
from datetime import date
import datetime
import dateparser
import babel.dates
from sqlalchemy import or_


from flask import Flask
from flask import render_template, redirect, request, url_for, session as flask_session
from flask_restful import Api, Resource, reqparse, abort, fields, inputs, marshal_with
from flask_assets import Environment, Bundle


from db import Session
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import func

from models import Event, Partner

app = Flask(__name__,static_url_path='/static')
api = Api(app)




assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle( 'base.scss','event.scss','shows.scss','collections.scss', filters='pyscss', output='all.css')
assets.register('scss_all', scss)



session = flask_scoped_session(Session, app)

def date_from_iso8601(date_str):
    return aniso8601.parse_date(date_str)

fields_map = {
    "text":fields.String,
    "date":fields.DateTime('iso8601'),
    "id":fields.Integer(default=None),
    "time":fields.String,
    }



event_field_defs = ([
    ('id'         ,{"field":"id",
                    "grp":0}),
    ('name'       ,{"field":"text",
                    "grp":1,
                    "required":True}),
    ('date'       ,{"field":"date",
                    "grp":1,
                    "required":True}),
    ('category'   ,{"field":"text",
                    "grp":1,
                    "required":True}),
    ('start'      ,{"field":"time",
                    "grp":1,}),
    ('end'        ,{"field":"time",
                    "grp":1}),
    ('description',{"field":"text",
                    "grp":1}),
    ('location'   ,{"field":"text",
                    "grp":1}),
    ('payment'  ,{"field":"text",
                  "grp":1}),
    ('notes'      ,{"field":"text",
                    "grp":1}),
    ('extlink'    ,{"field":"text",
                    "grp":2}),
    ('tickets'    ,{"field":"text",
                    "grp":2}),
    ('pri'        ,{"field":"text",
                    "grp":4}),
    ('recipe_num' ,{"field":"text",
                    "grp":5}),
    ('band_name'  ,{"field":"text",
                    "grp":5}),
    ('series'     ,{"field":"text",
                    "grp":5}),
    ('source'     ,{"field":"text",
                    "grp":5}),
    ('image'      ,{"field":"text",
                    "grp":5}),
    ('keywords'   ,{"field":"text",
                    "grp":5}),     
    ('category2'  ,{"field":"text",
                    "grp":5}),
    ('marketing'  ,{"field":"text",
                    "grp":5}),
    ('aero_email' ,{"field":"text",
                    "grp":5}),
    ('partner_email',{"field":"text",
                      "grp":5}),
    ('partner_name' ,{"field":"text",
                      "grp":5}),     
    ('pending'  ,{"field":"text",
                  "grp":5}),
    ('private'  ,{"field":"text",
                  "grp":5})
])

 



jinja_event_defs = [dict(name=k,**v) for k, v in event_field_defs] 
event_fields = dict( [(k,fields_map[v["field"]]) for k,v in event_field_defs])
event_parser = reqparse.RequestParser()


for k,data in event_field_defs:
    if data["field"] == "date":
        event_parser.add_argument(k,type =date_from_iso8601,required=True)
    if data["field"] == "text":
        event_parser.add_argument(k,required=True)
    if data["field"] == "time":
        event_parser.add_argument(k,required=True)



class EventResource(Resource):
    @marshal_with(event_fields)
    def get(self, id):
        obj = session.query(Event).get(id)
        if not obj: abort(404)
        return obj

    def delete(self, id):
        obj = session.query(Event).get(id)
        if not obj: abort(404)
        session.delete(obj)
        session.commit()
        return {}, 204

    @marshal_with(event_fields)
    def post(self, id):
        args = event_parser.parse_args()
        obj = session.query(Event).get(id)
        for key in args:
            setattr(obj, key, args[key])
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj, 201

class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):
        return session.query(Event).all()

    @marshal_with(event_fields)
    def post(self):
        args = event_parser.parse_args()
        obj = Event(**args)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj, 201


api.add_resource(EventListResource, '/api/events')
api.add_resource(EventResource,     '/api/events/<id>')







def format_datetime(value, format='short'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    elif format == 'short':
        format="MMM d"
    return babel.dates.format_datetime(value, format)

def format_time(value):
    if value =="":
        return "---"

    try:
        fields = value.split(":")
    
        hour24 = fields[0]
        minute = fields[1]
        ampm = "AM" if hour24 < 12 else "PM"
        return "{0}{1}{2}".format((int(hour24 )-1)%12 + 1,":{0}".format(int(minute)) if int(minute) !=0 else "", ampm)
    except Exception, e:
        return "--"
    

def weekday(value):
    #date = dateparser.parse(value)
    return babel.dates.format_datetime(value, "EE").lower()
    


app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['time'] = format_time
app.jinja_env.filters['weekday'] = weekday

from sqlalchemy.sql import extract


@app.route('/')
def index():
    filters = request.args.get('filters') or ["future"]
    #days = request.args.get('days')
    #categories = request.args.get("categories")


    events_q = session.query(Event)
    
    if "thismonth" in filters:
        current_time = datetime.datetime.utcnow()
        month_start = current_time - datetime.timedelta(days=current_time.day)
        events_q = events_q.filter(Event.date > month_start)
    if "thisweek" in filters:
        current_time = datetime.datetime.utcnow()
        week_start = current_time - datetime.timedelta(days=current_time.weekday())
        week_end = current_time - datetime.timedelta(days= current_time.weekday()-7)
        events_q = events_q.filter(Event.date > week_start).filter(Event.date <= week_end)
            
    if "public" in filters:
        events_q = events_q.filter(Event.private != "")
    if "duck" in filters:
        events_q = events_q.filter(Event.source == "duck")
    if "checks" in filters:
        events_q = events_q.filter(Event.payment !="")
    if "music" in filters:
        events_q = events_q.filter(Event.category == "music")
    if "future" in filters:
        events_q = events_q.filter(Event.date > datetime.datetime.utcnow())
    if "past" in filters:
        events_q = events_q.filter(Event.date < datetime.datetime.utcnow())
    if "day-sun" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 0)
    if "day-mon" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 1)
    if "day-tue" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 2)
    if "day-wed" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 3)
    if "day-thu" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 4)
    if "day-fri" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 5)
    if "day-sat" in filters:
        events_q = events_q.filter(extract('dow',Event.date) == 6)


        
        
        
        
    events = events_q.all()

    
    
    return render_template('events.html',
                           events=events,
                           page={"id":"index"},
                           )

@app.route('/shows')
def shows():
    events_q = session.query(Event)
    music_events = events_q.filter(or_(Event.category == 'show', Event.category == "music", Event.category=="band"))
    
    today = date.today()

    #day_start = date.today()
    #day_end = current_time + datetime.timedelta(days=1)
    #weekend_end = current_time + datetime.timedelta(days=7)
    #yesterday = current_time + datetime.timedelta(days=-1)


    future_events = music_events.filter(Event.date > today).all()


    weekday = today.weekday()
    #currently a weekend
    if weekday in [4,5,6]:
        weekend_start = today - datetime.timedelta(days = weekday - 4)
    #currently a weekeday
    else:
        weekend_start = today + datetime.timedelta(days = 4 - weekday)

    weekend_end = weekend_start + datetime.timedelta(days = 3)
    
    events_thisweekend = music_events\
                         .filter(Event.date >= weekend_start)\
                         .filter(Event.date <= weekend_end).all()
       
    events_today = music_events\
                   .filter(Event.date == today).all()
    


    return render_template('shows.html',
                           future_events=future_events,
                           events_today=events_today,
                           events_thisweekend=events_thisweekend,
                           page={"id":"shows"},
                           )




@app.route('/checks')
def checks():
    current_time = datetime.datetime.utcnow()
    week_start = current_time - datetime.timedelta(days=current_time.weekday())
    week_end = current_time - datetime.timedelta(days= current_time.weekday()-7)

 
    events = session.query(Event).filter(Event.date > week_start).filter(Event.date <= week_end).filter(Event.payment != "").all()
    return render_template('checks.html',
                           events=events,
                           page={"id":"checks",
                                 "week":week_start})
@app.route('/event/<id>')
def event(id):
    event = session.query(Event).get(id)
    return render_template('event.html',
                           event = event,
                           page={"id":"event"},
                           event_field_defs=jinja_event_defs)

@app.route('/new')
def new_event():
    return render_template('new-event.html',
                           page={"id":"new-event"},
                           event_field_defs=jinja_event_defs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
