from flask import request
from datetime import datetime
from flask_mysqldb import MySQL

mysql = MySQL()

def checkTraffic():
    cur = mysql.connection.cursor()
    visitor_ip = request.remote_addr
    today_date = datetime.now().date()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_at = created_at
    cur.execute("SELECT id FROM log WHERE visitor_ip = %s AND DATE(createdAt) = %s", (visitor_ip, today_date))
    existing_log = cur.fetchone()

    if existing_log is None:
        cur.execute("INSERT INTO log (visitor_ip, createdAt, updatedAt) VALUES (%s, %s, %s)", (visitor_ip, created_at, updated_at))
        mysql.connection.commit()

    cur.close()