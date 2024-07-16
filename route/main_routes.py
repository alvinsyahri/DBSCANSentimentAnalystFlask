from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from function import mains
from flask_mysqldb import MySQL

main_routes = Blueprint('main_routes', __name__)
mysql = MySQL()

@main_routes.route('/', methods = ['GET'])
def getMain():
    return render_template('page/pages-misc-under-maintenance.html')

@main_routes.route('/form-feedback', methods = ['GET'])
def getForm():
    mains.checkTraffic()
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT id, name FROM batch
            ORDER BY
                CASE
                    WHEN LEFT(name, 1) REGEXP '^[0-9]' THEN 1
                    ELSE 2
                END,
                name
        """)
    batchs = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    return render_template('page/form-feedback.html', batchs=batchs)

@main_routes.route('/form-feedback', methods = ['POST'])
def postForm():
    name = request.form['name']
    jalur_pembelajaran = request.form['jalur_pembelajaran']
    program = request.form['program']
    batch = request.form['batch']
    sesi = request.form['sesi']
    pembelajaran_pembahasan = request.form['pembelajaran_pengajaran']
    fasilitas_lingkungan = request.form['fasilitas_lingkungan']
    kepuasan_mentor = request.form['kepuasan_mentor']
    
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_at = created_at

    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO feedback (
            name, jalur_pembelajaran, program_id, batch_id, sesi, pembelajaran_pengajaran, 
            fasilitas_lingkungan, kepuasan_mentor, createdAt, updatedAt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        (
            name, jalur_pembelajaran, program, batch, sesi, pembelajaran_pembahasan, fasilitas_lingkungan, 
            kepuasan_mentor, created_at, updated_at
        )
    )
    
    feedback_id = cur.lastrowid
    # Terjemahkan teks untuk setiap kolom terkait
    translated_columns = {
        'translate_pembelajaran_pengajaran': pembelajaran_pembahasan,
        'translate_fasilitas_lingkungan': fasilitas_lingkungan,
        'translate_kepuasan_mentor': fasilitas_lingkungan
    }

    # Mengumpulkan hasil terjemahan
    translated_texts = {}
    for column, text in translated_columns.items():
        translated_texts[column] = mains.translate_text(text)

    # Menjalankan kueri untuk menyimpan data ke tabel translate_feedback
    cur.execute(
        """
        INSERT INTO translate_feedback (
        feedback_id, translate_pembelajaran_pengajaran, translate_fasilitas_lingkungan, 
        translate_kepuasan_mentor, createdAt, updatedAt) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """, 
        (
            feedback_id,
            translated_texts['translate_pembelajaran_pengajaran'],
            translated_texts['translate_fasilitas_lingkungan'],
            translated_texts['translate_kepuasan_mentor'],
            created_at,
            updated_at
        )
    )

    mysql.connection.commit()
    cur.close()

    return render_template('page/form-submit.html')

@main_routes.route('/get_programs', methods=['POST'])
def get_programs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, path FROM program ORDER BY createdAt DESC")
    programs = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    jalur_pembelajaran = request.form.get('jalur')
    if jalur_pembelajaran == 'Magang':
        filtered_programs = [program for program in programs if program[2] == 1]
    else:  # Jalur pembelajaran: Studi Independent
        filtered_programs = [program for program in programs if program[2] == 0]
    return jsonify(filtered_programs)
