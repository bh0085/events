#!/usr/bin/env python
import json, os, pprint
from models import Event

data_dir="_data"
def main():
    with open(os.path.join(data_dir,"events0.json")) as f:
        event_data = json.load(f)


#       
#   {u'band_name': None,
#u'category': u'music',
#u'category2': u'show',
#u'color': None,
#u'date': u'2017-05-13',
#u'description': u'',
#u'end': u'20:15:00',
#u'extlink': u'',
#u'image': None,
#u'keywords': u'',
#u'location': u'',
#u'marketing': None,
#u'name': u'Hope and Things',
#u'pri': 10,
#u'recipe_num': None,
#u'series': u'',
#u'source': u'special',
#u'start': u'19:30:00',
#u'tickets': u''}
    
    

if __name__=="__main__":
    main()
