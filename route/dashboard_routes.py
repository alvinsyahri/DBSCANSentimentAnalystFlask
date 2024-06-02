from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime, timedelta
from function import utils
from flask_mysqldb import MySQL
import json

dashboard_routes = Blueprint('dashboard_routes', __name__)
mysql = MySQL()

@dashboard_routes.route('/dashboard', methods = ['GET'])
def getDashboard():
    if 'username' in session:
        utils.checkTraffic()

        data = utils.grafis()

        # Mendapatkan tanggal hari ini dan kemarin
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        chartData = []
        chartLabels = []

        for record in data:
            # Mengonversi tanggal dari format string ke objek datetime
            record_date = datetime.strptime(str(record[0]), "%Y-%m-%d").date()
            
            # Membuat label untuk grafik berdasarkan tanggal
            if record_date == today:
                chartLabels.append("Hari Ini")
            elif record_date == yesterday:
                chartLabels.append("Kemarin")
            else:
                chartLabels.append(record_date.strftime("%d %b %Y"))
            
            # Menambahkan data record_count ke dalam chartData
            chartData.append(record[1])

        cur = mysql.connection.cursor()
        # Mengambil total record dari setiap tabel
        program_count = utils.get_total_records(cur, 'program')
        batch_count = utils.get_total_records(cur, 'batch')
        user_count = utils.get_total_records(cur, 'user')

        chartLabels_json = json.dumps(chartLabels)
        chartData_json = json.dumps(chartData)

        feedbacks = utils.newFeedback()

        mysql.connection.commit()
        cur.close()

        return render_template('page/dashboard.html', program_count=program_count, batch_count=batch_count, user_count=user_count, chartData=chartData_json, chartLabels=chartLabels_json, feedbacks=feedbacks,title='Dashboard - Analytics')
    else:
        return redirect('/login')
