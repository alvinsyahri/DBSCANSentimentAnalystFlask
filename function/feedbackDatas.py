from flask_mysqldb import MySQL

mysql = MySQL()

def get_feedback_data_from_database():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
        f.id, 
        f.name, 
        f.jalur_pembelajaran, 
        (SELECT p.name FROM program p WHERE p.id = f.program_id) AS program_name,
        (SELECT b.name FROM batch b WHERE b.id = f.batch_id) AS batch_name,
        f.sesi, 
        f.pembelajaran_pengajaran, 
        f.fasilitas_lingkungan, 
        f.kepuasan_mentor
    FROM 
        feedback f
    ORDER BY 
        f.createdAt DESC;
    """)
    feedbacks = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    return feedbacks

def convertProgram():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM program")
    feedbacks = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    # Buat dictionary untuk mapping
    mapping = {name: id for id, name in feedbacks}

    return mapping

def convertBatch():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM batch")
    batchs = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    # Inisialisasi dictionary untuk mapping
    mapping = {}

    # Iterasi dan tambahkan setiap pasangan (nama_batch, id_batch) ke dalam dictionary
    for id_batch, nama_batch in batchs:
        # Menambahkan entri dengan format 'Batch X'
        mapping[f'Batch {nama_batch}'] = id_batch
        # Menambahkan entri tanpa format 'Batch ' juga
        mapping[nama_batch] = id_batch

    return mapping
