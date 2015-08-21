from __future__ import division
import datetime
import requests
import time

url = 'http://jackcook.nyc'

requests_per_minute = 1 # move to config
graph_data_points = 360

def check_response():
    response = requests.get(url)
    ms = response.elapsed.microseconds / 1000
    return ms

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

with open('data.csv', 'a') as datafile:
    response_time = check_response()

    now = time.time()
    timestamp = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    datafile.write('%s,%.3f\n' % (timestamp, response_time))

with open('data.csv', 'r') as datafile:
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

    with open('month.csv', 'w+') as monthfile:
        monthfile.write(header)
        lines = parse_lines(month)
        for line in lines:
            monthfile.write(line)

    with open('week.csv', 'w+') as weekfile:
        weekfile.write(header)
        lines = parse_lines(week)
        for line in lines:
            weekfile.write(line)

    with open('day.csv', 'w+') as dayfile:
        dayfile.write(header)
        lines = parse_lines(day)
        for line in lines:
            dayfile.write(line)
