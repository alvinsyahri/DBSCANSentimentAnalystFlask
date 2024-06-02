from flask import Flask
from route import auth_routes, batch_routes, dashboard_routes, feedback_hasil_routes, feedback_data_routes, main_routes, program_routes, user_routes
from database import table
from datetime import timedelta
from flask_mysqldb import MySQL
 
app = Flask(__name__)
app.secret_key = 'skripsi-klastering-IL'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60*24)

# Cookie Configuration
global COOKIE_TIME_OUT

# MySQL Configuration
app.config['MYSQL_HOST'] = '8.222.232.107'
app.config['MYSQL_USER'] = 'alvin21'
app.config['MYSQL_PASSWORD'] = 'produk21kandang'
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
    app.run(host='0.0.0.0', port=5000)