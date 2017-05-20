#!/usr/bin/env python

import os
import json

import aniso8601
from datetime import date

from flask import Flask
from flask import render_template, redirect, request, url_for, session as flask_session
from flask_restful import Api, Resource, reqparse, abort, fields, inputs, marshal_with
from flask_assets import Environment, Bundle


from db import Session
from flask_sqlalchemy_session import flask_scoped_session

from models import Event, Partner

app = Flask(__name__)
api = Api(app)




assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('event.scss', 'base.scss', filters='pyscss', output='all.css')
assets.register('scss_all', scss)



session = flask_scoped_session(Session, app)

def date_from_iso8601(date_str):
    return aniso8601.parse_date(date_str)

fields_map = {
    "text":fields.String,
    "date":fields.DateTime('iso8601'),
    "id":fields.Integer(default=None)
    }



event_field_defs = {
    'id'        : "id",
    'date'      : "date",
    'name'      : "text",
    'category'  : "text",
    'category2' : "text",
    'description':"text",
    'end': "text",
    'extlink':"text",
    'image':"text",
    'keywords':"text",
    'location':"text",
    'pri':"text",
    'recipe_num':"text",
    'band_name':"text",
    'series':"text",
    'source':"text",
    'start':"text",
    'tickets':"text",
}

event_fields = dict( [(k,fields_map[v]) for k,v in event_field_defs.iteritems()])


event_parser = reqparse.RequestParser()
event_parser.add_argument('date',         type=date_from_iso8601,  required=True)
event_parser.add_argument('name',         type=str,   required=True)

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



@app.route('/')
def index():
    events = session.query(Event).all()
    return render_template('events.html', events=events, page={"id":"index"})

@app.route('/event/<id>',  methods=['GET', 'POST'])
def event(id):
    event = session.query(Event).get(id)
    return render_template('event.html',
                           event = event,
                           page={"id":"event"},
                           event_field_defs=event_field_defs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
