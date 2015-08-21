from __future__ import division
from datetime import datetime
from flask import Flask, render_template, url_for
from threading import Timer

import requests
import time

app = Flask(__name__)

url = 'http://jackcook.nyc'

requests_per_minute = 1 # move to config
graph_data_points = 360

def parse_lines(lines):
    total = 0
    i = -1
    newlines = []

    for line in lines[::-1]:
        requests_per_datapoint = int(len(lines) / graph_data_points)
        add = i % requests_per_datapoint == 0
        total += float(line.split(',')[1])
        i += 1
        if add:
            mean = total / requests_per_datapoint
            newline = '%s,%.5f\n' % (line.split(',')[0], mean)
            newlines.append(newline)
            total = 0.0

    return newlines

def web_response_check():
    print 'Checking web response time of %s' % url

    with open('./data.csv', 'a') as datafile:
        response = requests.get(url)
        response_time = response.elapsed.microseconds / 1000

        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        datafile.write('%s,%.3f\n' % (timestamp, response_time))

    with open('./data.csv', 'r') as datafile:
        month = []
        week = []
        day = []

        mmax = 60 * 24 * 30
        wmax = 60 * 24 * 7
        dmax = 60 * 24 * 1
        i = 0

        for line in datafile.readlines()[::-1]:
            if line[0] == 't':
                break

            try:
                if i < mmax:
                    month.append(line)

                if i < wmax:
                    week.append(line)

                if i < dmax:
                    day.append(line)
            except (IndexError):
                break

            i += 1

            if i == mmax:
                break

        header = 'time,response_time\n'

        with open('./static/month.csv', 'w+') as monthfile:
            monthfile.write(header)
            lines = parse_lines(month)
            for line in lines:
                monthfile.write(line)

        with open('./static/week.csv', 'w+') as weekfile:
            weekfile.write(header)
            lines = parse_lines(week)
            for line in lines:
                weekfile.write(line)

        with open('./static/day.csv', 'w+') as dayfile:
            dayfile.write(header)
            lines = parse_lines(day)
            for line in lines:
                dayfile.write(line)

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
    data = {'response_time': '89ms'}
    return render_template('index.html')

if __name__ == '__main__':
    print 'Starting up statusboard...'

    update()
    app.run()
