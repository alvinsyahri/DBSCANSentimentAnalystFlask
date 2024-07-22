from flask import Flask
from route import auth_routes, batch_routes, dashboard_routes, feedback_hasil_routes, feedback_data_routes, main_routes, program_routes, user_routes
from database import table
from flask_session import Session
import os
from datetime import timedelta
from flask_mysqldb import MySQL
 
app = Flask(__name__)
app.secret_key = 'skripsi-klastering-IL'

# Konfigurasi File-Based Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'sessions')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_THRESHOLD'] = 1000  # Batas maksimum file sesi
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Inisialisasi Session
server_session = Session(app)

# Cookie Configuration
global COOKIE_TIME_OUT

# MySQL Configuration
app.config['MYSQL_HOST'] = 'rm-gs5ug9n7utv3is0lxmo.mysql.singapore.rds.aliyuncs.com'
app.config['MYSQL_USER'] = 'alvin21'
app.config['MYSQL_PASSWORD'] = 'Putri12adiba'
app.config['MYSQL_DB'] = 'tugas_akhir'

mysql = MySQL(app)

table.create_table(app)

app.register_blueprint(main_routes.main_routes)
app.register_blueprint(dashboard_routes.dashboard_routes)
app.register_blueprint(feedback_data_routes.feedback_data_routes)
app.register_blueprint(feedback_hasil_routes.feedback_hasil_routes)
app.register_blueprint(batch_routes.batch_routes)
app.register_blueprint(program_routes.program_routes)
app.register_blueprint(user_routes.user_routes)
app.register_blueprint(auth_routes.auth_routes)

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True, port=5000)