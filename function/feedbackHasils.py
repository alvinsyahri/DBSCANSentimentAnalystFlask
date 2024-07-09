import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from textblob import TextBlob
from afinn import Afinn
from flask_mysqldb import MySQL
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

english_stemmer = SnowballStemmer('english')
mysql = MySQL()

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


def chekEpsMinRadius(data_scaled):
    # Tentukan rentang nilai untuk eps dan min_samples
    eps_range = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    min_samples_range = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    best_score = -1
    best_eps = None
    best_min_samples = None

    # Lakukan pencarian grid
    for eps in eps_range:
        for min_samples in min_samples_range:
            # Inisialisasi dan fit DBSCAN
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
            labels = dbscan.fit_predict(data_scaled)

            # Memastikan ada setidaknya dua kluster yang dihasilkan
            unique_labels = len(set(labels))
            if unique_labels <= 1:
                continue

            # Hitung silhouette score
            score = silhouette_score(data_scaled, labels, metric='euclidean')

            # Perbarui nilai terbaik jika ditemukan
            if score > best_score and len(set(labels)) == 4: # 4 kluster termasuk noise
                best_score = score
                best_eps = eps
                best_min_samples = min_samples

    return best_eps, best_min_samples, best_score