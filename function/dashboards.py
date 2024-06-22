from datetime import datetime, timedelta
from flask_mysqldb import MySQL

mysql = MySQL()

def grafis():
    cur = mysql.connection.cursor()

    # Tanggal mulai satu minggu yang lalu
    start_date = datetime.now() - timedelta(weeks=1)

    # Tanggal sekarang
    end_date = datetime.now()

    # Kueri untuk mendapatkan data grafis dari basis data
    cur.execute("""
        SELECT DATE(createdAt) as visit_date, COUNT(*) as record_count
        FROM log
        WHERE createdAt >= %s AND createdAt <= %s
            AND TIME(createdAt) >= '00:00:00' AND TIME(createdAt) <= '23:59:59'
        GROUP BY DATE(createdAt)
        ORDER BY DATE(createdAt) ASC
    """, (start_date, end_date))

    grafis_data = cur.fetchall()

    # Menutup kursor dan koneksi
    cur.close()
    cur.close()

    return grafis_data

def get_total_records(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) AS total_records FROM {table_name};")
    return cursor.fetchone()[0]

def newFeedback():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, pembelajaran_pengajaran FROM feedback ORDER BY createdAt DESC LIMIT 5 ")
    feedbacks = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return feedbacks