import os
import sqlite3

os.system('touch data.db')
db = sqlite3.connect('data.db')
db.execute('drop table if exists data')
db.execute('create table data (id integer primary key autoincrement, timestamp text not null, time real not null)')

with open('./data.csv', 'r') as f:
    for line in f:
        timestamp = line.split(',')[0]
        time = float(line.split(',')[1])
        db.execute('insert into data (timestamp, time) values (\'%s\', %f)' % (timestamp, time))

    db.commit()
