import mysql.connector
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Fungsi untuk koneksi ke database
def connect_to_mysql():
    try:
        # Ubah parameter sesuai dengan detail koneksi MySQL Anda
        connection = mysql.connector.connect(
            host="8.222.232.107",
            user="alvin21",
            password="produk21kandang",
            database="tugas_akhir"
        )
        return connection
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)
        return None

# Fungsi untuk menambahkan data ke tabel
def seed_data():
    try:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = created_at
        # Koneksi ke database
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            programs = [
                ('IBM Academy : Hybrid Cloud & Red Hat', 0),
                ('Game Design & Development', 0),
                ('IBM Academy : Advanced AI', 0),
                ('Android Mobile Development & UIUX Design', 0),
                ('Web Development & UIUX Design', 0),
                ('Web Developer', 1),
                ('Education Management', 1),
                ('Human Management', 1),
                ('Community & Acquisition', 1),
                ('Marketing Communications', 1),
                ('Strategic Project Officer', 1),
                ('Student Relation & Administration', 1),
                ('Information System Management Service', 1),
                ('Mobile Developer : Technical Writer', 1),
                ('Mobile Developer : Asisten Mentoring Tecnical', 1),
                ('Mobile Developer : Technical Researcher', 1),
                ('Photo & Video Editor', 1),
                ('Public Relation', 1),
                ('Event & Community', 1),
                ('Social Media Specialist', 1),
                ('Graphic Designer', 1),
                ('Game Developer', 1),
                ('UIUX Designer', 1),
                ('Research & Development', 1),
                ('Project Manager', 1),
            ]
            batches = ['1', '2', '3', '4', '5', '6', '7']

            users = [
                ('Alvin Syahri', 'alvin21', 'alvin21', 0),
                ('Admin Ganteng', 'admin', 'admin', 1),
            ]

            for program in programs:
                cursor.execute("INSERT INTO program (name, path, createdAt, updatedAt) VALUES (%s, %s, %s, %s)", (program[0], program[1], created_at, updated_at))
            for batch in batches:
                cursor.execute("INSERT INTO batch (name, createdAt, updatedAt) VALUES (%s, %s, %s)", (batch, created_at, updated_at))
            for user in users:
                hashed_password = bcrypt.generate_password_hash(user[2]).decode('utf-8')
                cursor.execute("INSERT INTO user (name, username, password, role, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s)", (user[0], user[1], hashed_password, user[3], created_at, updated_at))

            # Commit perubahan ke database
            connection.commit()
            print("Data seeded successfully.")

            # Tutup kursor dan koneksi
            cursor.close()
            connection.close()
    except Exception as e:
        print("Error while seeding data:", e)

# Panggil fungsi seed_data untuk menambahkan data ke tabel
seed_data()
