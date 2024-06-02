from flask import request
from datetime import datetime, timedelta
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.stem import SnowballStemmer
from textblob import TextBlob
from afinn import Afinn
english_stemmer = SnowballStemmer('english')
factory = StemmerFactory()
indonesian_stemmer = factory.create_stemmer()
from flask_mysqldb import MySQL

mysql = MySQL()

def get_total_records(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) AS total_records FROM {table_name};")
    return cursor.fetchone()[0]

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

def newFeedback():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, pembelajaran_pengajaran FROM feedback ORDER BY createdAt DESC LIMIT 5 ")
    feedbacks = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return feedbacks

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

def case_folding(text):
    if not isinstance(text, str):
        return ""
    
    # Lowercase the text
    text = text.lower()
    return text

def clean_text(text):
    # Remove unwanted patterns
    text = re.sub(r"@[\w]*", "", text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\b(rt|yg)\b', "", text)  # \b untuk mencocokkan batas kata
    text = re.sub(r'[!~]', "", text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'\.+', '', text)
    text = text.strip()
    
    return text

def tokenize_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    return tokens

def remove_stopwords(tokens):
    # Remove stopwords
    stopWord = set(stopwords.words('english'))
    filtered_tokens = [t for t in tokens if t not in stopWord]
    return filtered_tokens

def stem_tokens(tokens):
    # Stem tokens
    listWordAfterStemp = []
    for te in tokens:
        stemmingText = english_stemmer.stem(te)
        deleteExceptString = re.sub(r"[^a-z]", "", stemmingText)
        listWordAfterStemp.append(deleteExceptString)
    
    dataListWords = ' '.join(listWordAfterStemp)
    return dataListWords

def getPolarity(text):
    analysis = TextBlob(text)
    # try:
    #     analysis = analysis.translate(to="en")
    # except Exception as e:
    #     print(e)
        
    return analysis.sentiment.polarity

def getSubjectivity(text):
    analysis = TextBlob(text)
    # try:
    #     analysis = analysis.translate(to="en")
    # except Exception as e:
    #     print(e)
        
    return analysis.sentiment.subjectivity

def getAfinnScore(text):
    afinn = Afinn()
    # try:
    #     analysis = analysis.translate(to="en")
    # except Exception as e:
    #     print(e)
        
    return afinn.score(text)

def get_sentiment_label(cluster):
    if cluster == 0:
        return 'Positif'
    elif cluster == 1 or cluster == -1:
        return 'Netral'
    elif cluster == 2:
        return 'Negatif'
    else:
        return 'Unknown'

def fetch_klusters(sentimen, user_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT kluster.kluster, kluster.feedback,
            (SELECT name FROM feedback WHERE id = kluster.feedback_id) AS feedback_name,
            (SELECT jalur_pembelajaran FROM feedback WHERE id = kluster.feedback_id) AS jalur_pembelajaran,
            (SELECT sesi FROM feedback WHERE id = kluster.feedback_id) AS sesi,
            (SELECT name FROM program WHERE id = (SELECT program_id FROM feedback WHERE id = kluster.feedback_id)) AS program_name,
            (SELECT name FROM batch WHERE id = (SELECT batch_id FROM feedback WHERE id = kluster.feedback_id)) AS batch_name
        FROM kluster
        WHERE kluster.kluster = %s AND kluster.user_id = %s
        ORDER BY kluster.createdAt DESC;
    """, (sentimen, user_id))
    klusters = cur.fetchall()

    mysql.connection.commit()
    cur.close()

    return klusters

def get_top_programs(klusters):
    df = pd.DataFrame(klusters, columns=['kluster', 'feedback', 'feedback_name', 'jalur_pembelajaran', 'sesi', 'program', 'batch'])
    
    count_per_program = df['program'].value_counts()

    top_programs = count_per_program.nlargest(7)

    labels = top_programs.index.tolist()
    values = top_programs.values.tolist()

    return labels, values

def get_top_batch(klusters):
    df = pd.DataFrame(klusters, columns=['kluster', 'feedback', 'feedback_name', 'jalur_pembelajaran', 'sesi', 'program', 'batch'])
    
    count_per_batch = df['batch'].value_counts()

    top_batchs = count_per_batch.nlargest(5)

    labels = ["Batch " + str(batch) for batch in top_batchs.index.tolist()]
    values = top_batchs.values.tolist()

    return labels, values

def get_feedback_kluster_from_database(user_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT kluster.kluster, kluster.feedback,
            (SELECT name FROM feedback WHERE id = kluster.feedback_id) AS feedback_name,
            (SELECT jalur_pembelajaran FROM feedback WHERE id = kluster.feedback_id) AS jalur_pembelajaran,
            (SELECT sesi FROM feedback WHERE id = kluster.feedback_id) AS sesi,
            (SELECT name FROM program WHERE id = (SELECT program_id FROM feedback WHERE id = kluster.feedback_id)) AS program_name,
            (SELECT name FROM batch WHERE id = (SELECT batch_id FROM feedback WHERE id = kluster.feedback_id)) AS batch_name
        FROM kluster
        WHERE kluster.user_id = %s
        ORDER BY kluster.createdAt DESC;
    """, (user_id,))
    klusters = cur.fetchall()

    mysql.connection.commit()
    cur.close()

    return klusters
