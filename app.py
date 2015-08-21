from __future__ import division
from contextlib import closing
from datetime import datetime
from flask import Flask, Response, flash, g, render_template, url_for
from threading import Timer

import sqlite3
import requests
import time

DATABASE = 'data.db'
SECRET_KEY = 'statusboardkey'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

url = 'http://jackcook.nyc'

requests_per_minute = 1 # move to config
graph_data_points = 360

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

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

def web_response_check():
    print 'Checking web response time of %s' % url

    response = requests.get(url)
    response_time = response.elapsed.microseconds / 1000

    now = time.time()
    timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

    db = connect_db()
    db.execute('insert into data (timestamp, time) values (\'%s\', %.3f)' % (timestamp, response_time))
    db.commit()
    db.close()

    print '%s returned in %.3fms' % (url, response_time)

@app.route('/data')
def get_data():
    objects = g.db.execute('select timestamp, time from data order by id desc limit 1440')
    data = parse_data([dict(timestamp=row[0], time=row[1]) for row in objects.fetchall()][::-1])

    returnstr = 'timestamp,time\n'

    for datum in data:
        returnstr += '%s,%.5f\n' % (datum['timestamp'], datum['time'])

    return Response(returnstr, mimetype='text/csv')

done = False

def update():
    global done

    second = datetime.now().second

    if second < 2 and not done:
        web_response_check()
        done = True
    elif second > 58:
        done = False

    timer = Timer(0.1, update)
    timer.daemon = True
    timer.start()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print 'Starting up statusboard...'

    init_db()

    update()
    app.run(host='0.0.0.0', port=5000)
