from __future__ import division
from contextlib import closing
from datetime import datetime, timedelta
from flask import Flask, Response, g, render_template, request, url_for
from threading import Timer

import json
import sqlite3

from checks import Check
from checks import PingCheck
from checks import WebResponseCheck

URL = 'http://jackcook.nyc'

app = Flask(__name__)
app.config.from_object(__name__)

requests_per_minute = 1 # move to config
graph_data_points = 360

checks = []

def connect_db():
    return sqlite3.connect('data.db')

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def parse_data(data):
    total = 0
    i = -1
    newdata = []

    for datum in data:
        requests_per_datapoint = int(len(data) / graph_data_points)
        requests_per_datapoint = requests_per_datapoint if requests_per_datapoint is not 0 else 1
        add = i % requests_per_datapoint == 0
        total += float(datum['time'])
        i += 1
        if add:
            mean = total / requests_per_datapoint
            newdatum = {'timestamp': datum['timestamp'], 'time': mean}
            newdata.append(newdatum)
            total = 0.0

    return newdata

@app.route('/')
def index():
    global checks
    return render_template('index.html', checks=checks)

@app.route('/data')
def get_data():
    q = request.args.get('q')
    limit = 0

    if q == 'day':
        limit = 60 * 24
    elif q == 'week':
        limit = 60 * 24 * 7
    elif q == 'month':
        limit = 60 * 24 * 30

    objects = g.db.execute('select timestamp, time from %s order by id desc limit %d' % (request.args.get('t'), limit))
    data = parse_data([dict(timestamp=row[0], time=row[1]) for row in objects.fetchall()][::-1])

    returnstr = 'timestamp,time\n'

    for datum in data:
        current = datetime.now()
        timestamp = datetime.strptime(datum['timestamp'], '%Y-%m-%d %H:%M:%S')
        last = current - timedelta(minutes=limit)

        if last > timestamp: # if timestamp is older than the limit requested
            pass
        else:
            returnstr += '%s,%.5f\n' % (datum['timestamp'], datum['time'])

    return Response(returnstr, mimetype='text/csv')

def load_checks():
    global checks

    db = connect_db()

    with open('config.json') as config_file:
        data = json.load(config_file)
        config_checks = data['checks']

        for config_check in config_checks:
            if config_check['type'] == 'web_response':
                check = WebResponseCheck(config_check['id'], config_check['payload'])
                checks.append(check)

                db.execute('create table if not exists check%s (id integer primary key autoincrement, timestamp text not null, time text not null)' % config_check['id'])

        db.commit()
        db.close()

done = False

def update():
    global checks
    global done

    second = datetime.now().second

    if second == 0 and not done:
        print 'Performing %d checks...' % len(checks)

        for check in checks:
            check.perform_check(connect_db())

        done = True
    elif second > 58:
        done = False

    timer = Timer(0.1, update)
    timer.daemon = True
    timer.start()

if __name__ == '__main__':
    print 'Starting up statusboard...'

    load_checks()
    update()

    # app.debug = True # debug mode causes checks to be run twice for some reason
    app.run(host='0.0.0.0', port=5000)
