from __future__ import division
from contextlib import closing
from datetime import datetime
from flask import Flask, Response, g, render_template, request, url_for
from threading import Timer

import sqlite3

from checks import Check
from checks import WebResponse

URL = 'http://jackcook.nyc'

app = Flask(__name__)
app.config.from_object(__name__)

requests_per_minute = 1 # move to config
graph_data_points = 360

checks = []

def connect_db():
    return sqlite3.connect('data.db')

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

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
    return render_template('index.html')

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

    objects = g.db.execute('select timestamp, time from data order by id desc limit %d' % limit)
    data = parse_data([dict(timestamp=row[0], time=row[1]) for row in objects.fetchall()][::-1])

    returnstr = 'timestamp,time\n'

    for datum in data:
        returnstr += '%s,%.5f\n' % (datum['timestamp'], datum['time'])

    return Response(returnstr, mimetype='text/csv')

done = False

def update():
    global checks
    global done

    second = datetime.now().second

    if second < 2 and not done:
        if len(checks) == 0:
            check = WebResponse(app.config['URL'])
            checks.append(check)

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

    init_db()
    update()
    app.run(host='0.0.0.0', port=5000)
