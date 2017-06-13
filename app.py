#!/usr/bin/env python

import os
import json
from collections import OrderedDict
import aniso8601
from datetime import date, timedelta
import datetime
import dateparser, urllib2
from operator import itemgetter


from sqlalchemy import or_

from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from flask import render_template, redirect, request, url_for, session as flask_session
from flask_restful import Api, Resource, reqparse, abort, fields, inputs, marshal_with
from flask_assets import Environment, Bundle

from flask_migrate import Migrate


from db import Session
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import func

from models import Event, Partner, db2

bookings = Blueprint('bookings', __name__,
               template_folder='templates')



app = Flask(__name__,static_url_path='/bookings/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./events.db'


api = Api(bookings)


db2.init_app(app) 
migrate = Migrate(app, db2)

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
    "na":fields.String,
    "bool":fields.Boolean, 
    "select":fields.String,
    "textarea":fields.String
    }



event_field_defs = ([
    ('id'         ,{"field":"id",
                    "grp":5}),
    ('category'   ,{"field":"select",
                    "grp":1,
                    "required":True}),
    ('name'       ,{"field":"text",
                    "grp":1,
                    "required":True}),
    
    ('band_name'  ,{"field":"text",
                    "grp":1,
                    "typeahead":"/bookings/bandnames",
                    "alternates":"name",
                    "triggertype":"select",
                    "triggername":"category",
                    "triggervalue":"band"}),
    ('date'       ,{"field":"date",
                    "grp":1,
                    "required":True}),
    ('start'      ,{"field":"time",
                    "grp":1,}),
    ('end'        ,{"field":"time",
                    "grp":1}),
    ('location'   ,{"field":"select",
                    "grp":2,
                    "required":True}),
    ('series'     ,{"field":"select",
                    "grp":2}),
    ('offsite_address',{"field":"text",
                        "grp":"2a"}),
    ('offsite_name',{"field":"text",
                     "grp":"2a"}),
    ('series_name',{"field":"text",
                        "grp":5}),
    
    ('private_invoiceamount',{"field":"text",
                              "grp":"2c"}),
    
    ('private_invoicepaid',{"field":"bool",
                              "grp":"2c"}),
    
    ('private_numguests',{"field":"text",
                              "grp":"2c"}),
    
    ('private_barminimum',{"field":"text",
                              "grp":"2c"}),

    ('private_invoicenum',{"field":"text",
                              "grp":"2c"}),
    
    ('private_eventtype',{"field":"text",
                              "grp":"2c"}),
    ('description',{"field":"text",
                    "grp":1}),
    ('payment'  ,{"field":"text",
                  "grp":3}),
    ('notes'      ,{"field":"textarea",
                    "grp":3}),
    ('extlink'    ,{"field":"text",
                    "grp":3}),
    ('tickets'    ,{"field":"text",
                    "grp":3}),
    ('partner_email',{"field":"text",
                      "grp":3}),
    ('partner_name' ,{"field":"text",
                      "grp":3}),
    ('pending'  ,{"field":"bool",
                  "grp":4}),
    ('private'  ,{"field":"bool",
                  "grp":2}),
    ('recipe_num' ,{"field":"text",
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
    ('created_user',{"field":"na",
                     "grp":5}),
    ('updated_user',{"field":"na",
                     "grp":5}),
    ('created',{"field":"na",
                "grp":5}),
    ('updated',{"field":"na",
                "grp":5}),

    
     
])

 



jinja_event_defs = [dict(name=k,**v) for k, v in event_field_defs] 
event_fields = dict( [(k,fields_map[v["field"]]) for k,v in event_field_defs])
event_fields["pri"] = fields.String
             
event_parser = reqparse.RequestParser()


for k,data in event_field_defs:
    if data["field"] == "date":
        event_parser.add_argument(k,type =date_from_iso8601,required=True)
    if data["field"] == "text":
        event_parser.add_argument(k,required=True)
    if data["field"] == "select":
        event_parser.add_argument(k,required=True)
    if data["field"] == "time":
        event_parser.add_argument(k,required=True)
    if data["field"] == "bool":
        event_parser.add_argument(k,type=lambda x: True if int(x) > 0 else False ,required=True)
    if data["field"] == "textarea":
        event_parser.add_argument(k,required=True)
                



class EventResource(Resource):
    @marshal_with(event_fields)
    def get(self, id):
        obj = session.query(Event).get(id)
       
        if not obj: abort(404)
        if obj.deleted: abort(404)
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

        name = request.headers.get('X-Forwarded-User', "debug")
        obj.updated_user = name
        obj.updated =datetime.datetime.now()
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj, 201

class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):

        filters = request.args.get('filters') or ["all"]
        public = request.args.get('public')

        query = session.query(Event).filter(Event.deleted != True)
        
        if "calendar" in filters:
            start_date = date.today() -timedelta(days = 7)
            query = query.filter(Event.date >= start_date)

        if "past" in filters:
            end_date = date.today() + timedelta(days = 7)
            query = query.filter(Event.date < end_date)

        events = query.order_by(Event.date, Event.start).all()

        if public=="true":
            filtered_events = [e for e in events if not (e.private or e.pending)]

            print len(filtered_events)
            print filtered_events[0]
    
            public_keys =['date', 'name', 'start', 'end', 'description', 'location', 'category', 'extlink', 'tickets', 'pri', 'source',"recipe_num", "band_name", "keywords", "category", "image", "series", "category2"]
            
            public_events = [dict((k, getattr(e,k)) for k in public_keys) for e in filtered_events]

            public_events.sort(key=itemgetter('end'))
            public_events.sort(key=itemgetter('start'))
            public_events.sort(key=itemgetter('pri'))
            public_events.sort(key=itemgetter('date'))
            
            return public_events

        else:
            return events

        

    @marshal_with(event_fields)
    def post(self):


        #raise
        #return 'Ohnoes'
        #prs0 = reqparse.RequestParser()
        #sample_args = prs0.parse_args()
        #raise Exception()

        args = event_parser.parse_args()
        
        
        obj = Event(**args)



        name = request.headers.get('X-Forwarded-User', "debug")
        obj.updated_user = name
        obj.updated =datetime.datetime.now()
        obj.created_user = name
        obj.created =datetime.datetime.now()
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        
        return obj, 201


api.add_resource(EventListResource, '/api/events')
api.add_resource(EventResource,     '/api/events/<id>')







def format_datetime(value, fmt='short'):
    #if fmt == 'full':
    #    fmt="EEEE, d. MMMM y 'at' HH:mm"
    #elif fmt == 'medium':
    #    fmt="EE dd.MM.y HH:mm"
    #elif fmt == 'short':
    #    fmt="MMM d"
    #return babel.dates.format_datetime(value, fmt)
    return value.strftime("%m %d")
    
def format_time(value):
    if value =="":
        return "---"

    try:
        fields = value.split(":")
    
        hour24 = int(fields[0])
        minute = int(fields[1])
        ampm = "AM" if hour24 < 12 else "PM"
        return "{0}{1}{2}".format((int(hour24 )-1)%12 + 1,":{0}".format(int(minute)) if int(minute) !=0 else "", ampm)
    except Exception, e:
        return "--"
    

def weekday(value):
    #date = dateparser.parse(value)
    #return babel.dates.format_datetime(value, "EE").lower()
    return value.strftime("%a").lower()

def sortgroups(grouplist):
    return sorted(grouplist, key = lambda x:str( x.grouper)[0])

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['time'] = format_time
app.jinja_env.filters['weekday'] = weekday
app.jinja_env.filters['sortgroups'] = sortgroups


from sqlalchemy.sql import extract

@bookings.route('/bandnames')
def bandnames():
    data =json.load( urllib2.urlopen("http://52.70.165.218:5052/bandnames.json"))
    return jsonify(data)
    


@bookings.route('/')
def index():
    filters = request.args.get('filters') or ["future"]
    #days = request.args.get('days')
    #categories = request.args.get("categories")

    print 'The URL for this page is {}'.format(url_for('bookings.index'))


    events_q = session.query(Event).filter(Event.deleted!= True)
    
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
        events_q = events_q.filter(Event.date >= date.today())
    if "past" in filters:
        events_q = events_q.filter(Event.date < date.today())
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
    events = sorted( events, key = lambda  x:x.start)
    events = sorted( events, key = lambda x:x.pri)
    
    
    return render_template('events.html',
                           events=events,
                           page={"id":"index"},
                           )

@bookings.route('/shows')
def shows():
    events_q = session.query(Event).filter(Event.deleted != True)
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



    

@bookings.route('/checks')
def checks():
    current_time = datetime.datetime.utcnow()
    week_start = current_time - datetime.timedelta(days=current_time.weekday())
    week_end = current_time - datetime.timedelta(days= current_time.weekday()-7)

 
    events = session.query(Event).filter(Event.deleted != True).filter(Event.date > week_start).filter(Event.date <= week_end).filter(Event.payment != "").all()
    return render_template('checks.html',
                           events=events,
                           page={"id":"checks",
                                 "week":week_start})

event_categories = [
    "",
    "beer",
    "food",
    "trivia",
    "feature",
    "band",
    "talk",
    "dj",
    "bike",
    "art",
    "chocolate",
    "videogames",
    "modified hours",
    "closed",
    "other"
]

locations = [
    "",
    "foods-hub",
    "taproom-brewery",
    "taproom-entry",
    "taproom-tables",
    "full-site",
    "offsite",
    "other",
]


series = [
    "",
    "allseries",
    "bbb",
    "biketalk",
    "boardgames",
    "boycott",
    "byop",
    "calendar",
    "djs",
    "duckday",
    "duckheadliner",
    "ducksalon",
    "ducktalk",
    "duckvillage",
    "forrest",
    "funkflights",
    "latenight",
    "latenitebites",
    "monday",
    "pindrop",
    "freeform fun",
    "silentmovies",
    "trivia",
    "weekend",
    "css",
    "closed",
    "shows",
    "community",
    "beers",
    "misc",
    "karaoke",
    "special"
]

event_grp_defs ={
    1:{"name":"public info"},
    2:{"name":"internal info"},
    "2a":{"name":"offsite event info",
          "type":"hidden",
          "triggername":"location",
          "triggertype":"selection",
          "triggervalue":"offsite"},
    "1b":{"name":"band details",
          "type":"hidden",
          "triggername":"category",
          "triggertype":"selection",
          "triggervalue":"band"},    
    "2c":{"name":"private event info",
          "type":"hidden",
          "triggername":"private",
          "triggertype":"selection",
          "triggervalue":"1"},
    3:{"name":"partner"},
    4:{"name":"flags"},
    5:{"name":""}
}



@bookings.route("/event/delete/<eventid>", methods=['GET', 'POST'])
def delete_event(eventid):
    obj = session.query(Event).get(eventid)
    if not obj: abort(404)
    obj.deleted = True;
    session.commit()
    print obj.deleted
    return ""
    
@bookings.route('/event/<id>')
def event(id):
    event = session.query(Event).get(id)
    return render_template('event.html',
                           event = event,
                           page={"id":"event"},
                           event_field_defs=jinja_event_defs,
                           selects={"category":event_categories,
                                    "location":locations,
                                    "series":series},
                           group_defs = event_grp_defs)

@bookings.route('/new')
def new_event():
    return render_template('new-event.html',
                           page={"id":"new-event"},
                           event_field_defs=jinja_event_defs,
                           selects={"category":event_categories,
                                    "location":locations,
                                    "series":series},
                           group_defs = event_grp_defs)



app.register_blueprint(bookings, url_prefix='/bookings')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = "debug launcher")
    parser.add_argument('--debug', dest="debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        app.run( debug=True, host='0.0.0.0', port=5000)
    else:
        app.run( host='0.0.0.0', port=5000)
