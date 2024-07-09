from flask_mysqldb import MySQL

mysql = MySQL()

def create_table(app):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                username VARCHAR(30) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role BOOLEAN NOT NULL,
                createdAt DATETIME,
                updatedAt DATETIME
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS program (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                path BOOLEAN,
                createdAt DATETIME,
                updatedAt DATETIME
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS batch (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                createdAt DATETIME,
                updatedAt DATETIME
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                visitor_ip VARCHAR(30) NOT NULL,
                createdAt DATETIME,
                updatedAt DATETIME
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                jalur_pembelajaran VARCHAR(20) NOT NULL,
                program_id INT NOT NULL,
                batch_id INT NOT NULL,
                sesi VARCHAR(20) NOT NULL,
                pembelajaran_pengajaran TEXT NOT NULL,
                fasilitas_lingkungan TEXT NOT NULL,
                kepuasan_mentor TEXT NOT NULL,
                createdAt DATETIME,
                updatedAt DATETIME,
                CONSTRAINT fk_program
                    FOREIGN KEY (program_id) 
                    REFERENCES program(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                CONSTRAINT fk_batch
                    FOREIGN KEY (batch_id) 
                    REFERENCES batch(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS kluster (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kluster VARCHAR(15) NOT NULL,
                feedback TEXT NOT NULL,
                user_id INT NOT NULL,
                feedback_id INT NOT NULL,
                createdAt DATETIME,
                updatedAt DATETIME,
                CONSTRAINT fk_user
                    FOREIGN KEY (user_id) 
                    REFERENCES user(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                CONSTRAINT fk_feedback
                    FOREIGN KEY (feedback_id) 
                    REFERENCES feedback(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS translate_feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                feedback_id INT NOT NULL,
                translate_pembelajaran_pengajaran TEXT NOT NULL,
                translate_fasilitas_lingkungan TEXT NOT NULL,
                translate_kepuasan_mentor TEXT NOT NULL,
                createdAt DATETIME,
                updatedAt DATETIME,
                CONSTRAINT ts_feedback
                    FOREIGN KEY (feedback_id) 
                    REFERENCES feedback(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );
        ''')
        mysql.connection.commit()
        cur.close()