#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from datetime import datetime

from . import config
from .models import Pokemon, Gym, Pokestop


class Pogom(Flask):
    def __init__(self, import_name, **kwargs):
        super(Pogom, self).__init__(import_name, **kwargs)
        self.json_encoder = CustomJSONEncoder
        self.route("/", methods=['GET'])(self.fullmap)
        self.route("/raw_data", methods=['GET'])(self.raw_data)
        self.route("/next_loc", methods=['POST'])(self.next_loc)

    def fullmap(self):
        return render_template('map.html',
                               lat=config['ORIGINAL_LATITUDE'],
                               lng=config['ORIGINAL_LONGITUDE'],
                               gmaps_key=config['GMAPS_KEY'],
                               lang=config['LOCALE'])

    def raw_data(self):
        d = {}
        if request.args.get('pokemon', 'true') == 'true':
            d['pokemons'] = Pokemon.get_active()

        if request.args.get('pokestops', 'false') == 'true':
            d['pokestops'] = Pokestop.get_all()

        if request.args.get('gyms', 'true') == 'true':
            d['gyms'] = Gym.get_all()

        return jsonify(d)

    def next_loc(self):
        lat = request.values.get('lat', type=float)
        lon = request.values.get('lon', type=float)
        location = request.values.get('location', type=str)
        if not ((lat and lon) or location):
            print('[-] Invalid next location: %s,%s' % (lat, lon))
            return 'bad parameters', 400
        else:
            if location:
                position = get_pos_by_name(location)
                lat = position[0]
                lon = position[1]
            config['ORIGINAL_LATITUDE'] = lat
            config['ORIGINAL_LONGITUDE'] = lon
            return 'ok'


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
