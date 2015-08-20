from __future__ import division
import datetime
import requests
import time

url = 'http://jackcook.nyc'

def check_response():
    response = requests.get(url)
    ms = response.elapsed.microseconds / 1000
    return ms

with open('data.csv', 'a') as datafile:
    response_time = check_response()

    now = time.time()
    timestamp = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    datafile.write('%s,%.3f\n' % (timestamp, response_time))

with open('data.csv', 'r') as datafile:
    month = []
    week = []
    day = []

    mmax = 60 * 24 * 28
    wmax = 60 * 24 * 7
    dmax = 60 * 24 * 1
    i = 0

    for line in datafile:
        if i == 0:
            i += 1
            continue
        else:
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
        for line in month:
            monthfile.write(line)

    with open('week.csv', 'w+') as weekfile:
        weekfile.write(header)
        for line in week:
            weekfile.write(line)

    with open('day.csv', 'w+') as dayfile:
        dayfile.write(header)
        for line in day:
            dayfile.write(line)
