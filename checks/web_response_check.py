from __future__ import division
from check import Check
from datetime import datetime

import requests
import sqlite3
import time

class WebResponseCheck(Check):
    def __init__(self, id, url):
        self.id = id
        self.url = url

    def perform_check(self, db):
        print 'Checking web response time of %s...' % self.url

        response = requests.get(self.url)
        response_time = response.elapsed.microseconds / 1000

        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

        try:
            db.execute('insert into check%d (timestamp, time) values (\'%s\', %.3f)' % (self.id, timestamp, response_time))
        except:
            db.execute('create table check%d (id integer primary key autoincrement, timestamp text not null, time text not null)' % self.id)
            db.execute('insert into check%d (timestamp, time) values (\'%s\', %.3f)' % (self.id, timestamp, response_time))

        db.commit()
        db.close()

        print '%s returned in %.3fms' % (self.url, response_time)
