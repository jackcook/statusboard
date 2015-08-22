from __future__ import division
from check import Check
from datetime import datetime

import ping
import sqlite3
import time

class PingCheck(Check):
    def __init__(self, ip):
        self.ip = ip

    def perform_check(self, db):
        print 'Pinging %s...' % self.ip

        response = ping.quiet_ping(self.ip, count=8) # put count in config
        response_time = response[2] # returns (percent_lost, max round trip time, average round trip time)

        now = time.time()
        timestamp = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

        db.execute('insert into ping (timestamp, time) values (\'%s\', %.3f)' % (timestamp, response_time))
        db.commit()
        db.close()

        print '%s returned ping in %.3fms' % (self.ip, response_time)
