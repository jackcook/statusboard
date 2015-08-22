from __future__ import division
from check import Check
from datetime import datetime

import requests
import sqlite3
import time

class WebResponse(Check):
    def __init__(self, url):
        self.url = url

    def perform_check(self, db):
        print 'Checking web response time of %s' % self.url

        response = requests.get(self.url)
        response_time = response.elapsed.microseconds / 1000

        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

        db.execute('insert into data (timestamp, time) values (\'%s\', %.3f)' % (timestamp, response_time))
        db.commit()
        db.close()

        print '%s returned in %.3fms' % (self.url, response_time)
