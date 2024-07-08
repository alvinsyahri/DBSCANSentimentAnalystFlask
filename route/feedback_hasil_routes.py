from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import pandas as pd
from datetime import datetime
from function import feedbackHasils
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from flask_mysqldb import MySQL

feedback_hasil_routes = Blueprint('feedback_hasil_routes', __name__)
mysql = MySQL()

@feedback_hasil_routes.route('/dashboard/feedback/hasil', methods = ['GET'])
def getFeedbackHasil():
    if 'username' in session:
        klustersPositif = feedbackHasils.fetch_klusters('Positif', session['user_id'])
        klustersNegatif = feedbackHasils.fetch_klusters('Negatif', session['user_id'])
        klustersNetral = feedbackHasils.fetch_klusters('Netral', session['user_id'])
        

        labels_doughnut_positif, values_doughnut_positif = feedbackHasils.get_top_programs(klustersPositif)
        labels_doughnut_negatif, values_doughnut_negatif = feedbackHasils.get_top_programs(klustersNegatif)
        labels_doughnut_netral, values_doughnut_netral = feedbackHasils.get_top_programs(klustersNetral)

        labels_bar_positif, values_bar_positif = feedbackHasils.get_top_batch(klustersPositif)
        labels_bar_negatif, values_bar_negatif = feedbackHasils.get_top_batch(klustersNegatif)
        labels_bar_netral, values_bar_netral = feedbackHasils.get_top_batch(klustersNetral)
        
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT kluster, COUNT(*) AS jumlah_record FROM kluster WHERE kluster IN ('Positif', 'Negatif', 'Netral') AND user_id = { session['user_id']} GROUP BY kluster")
        grafis = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        tabs = [
            {'id': 'positif', 'label': 'Positif', 'charts': ['myChart2', 'myChart3'], 'name': ['Batch', 'Program'], 'table_id': 'myTable1', 'klusters': klustersPositif},
            {'id': 'negatif', 'label': 'Negatif', 'charts': ['myChart4', 'myChart5'], 'name': ['Batch', 'Program'], 'table_id': 'myTable2', 'klusters': klustersNegatif},
            {'id': 'netral', 'label': 'Netral', 'charts': ['myChart6', 'myChart7'], 'name': ['Batch', 'Program'], 'table_id': 'myTable3', 'klusters': klustersNetral}
        ]

        labels = [item[0] for item in grafis]
        values = [item[1] for item in grafis]
        grafis = [
            labels,
            values
        ]

        silhouette_score = session.get('silhouette_score')
        
        return render_template('page/feedback/hasil.html', title='Hasil Klasterisasi Feedback', 
                               tabs=tabs, 
                               labels_doughnut_positif=labels_doughnut_positif, 
                               labels_doughnut_negatif=labels_doughnut_negatif, 
                               labels_doughnut_netral=labels_doughnut_netral, 
                               values_doughnut_positif=values_doughnut_positif, 
                               values_doughnut_negatif=values_doughnut_negatif, 
                               values_doughnut_netral=values_doughnut_netral, 
                               labels_bar_positif=labels_bar_positif, 
                               labels_bar_negatif=labels_bar_negatif, 
                               labels_bar_netral=labels_bar_netral, 
                               values_bar_positif=values_bar_positif,   
                               values_bar_negatif=values_bar_negatif, 
                               values_bar_netral=values_bar_netral, 
                               grafis=grafis,
                               silhouette_score=silhouette_score)
    else:
        return redirect('/login')
    
@feedback_hasil_routes.route('/dashboard/feedback/hasil', methods=['POST'])
def postFeedbackHasil():
    # catch data feedback choice
    mappingChoice = {
        'Pembelajaran dan Pengajaran': 'pembelajaran_pengajaran',
        'Fasilitas dan Lingkungan': 'fasilitas_lingkungan',
        'Kepuasan terhadap Mentor': 'kepuasan_mentor'
    }

    choice = request.form['choice']
    for key, value in mappingChoice.items():
        choice = choice.replace(key, value)

    # hit database
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT id, {choice} FROM feedback")
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    # check data empty
    if len(data) == 0:
        flash('Data Feedback Kosong, Gagal Di Kluster', 'danger')
        return redirect(url_for('feedback_hasil_routes.postFeedbackHasil'))
    else:
        # convert tuple to dictionary form access by row now access by coloumn
        dictionary = {
                'id': [subtuple[0] for subtuple in data],
                'text': [subtuple[1] for subtuple in data]
            }

        # convert dataframe dan delete row when nan or empty string


        data = pd.DataFrame(dictionary)
        data['translated'] = data['text'].apply(feedbackHasils.translate_text)

        data.replace('', pd.NA, inplace=True)

        data = data.dropna(how='any')

        # prepossesing
        data['case folding'] = data['translated'].apply(feedbackHasils.case_folding)
        data['cleaning data'] = data['case folding'].apply(feedbackHasils.clean_text)
        data['tokenize'] = data['cleaning data'].apply(feedbackHasils.tokenize_text)
        data['stopwords'] = data['tokenize'].apply(feedbackHasils.remove_stopwords)
        data['stemming'] = data['stopwords'].apply(feedbackHasils.stem_tokens)

        # scoring sentiment
        data['polarity'] = data['stemming'].apply(feedbackHasils.getPolarity)
        data['subjectivity'] = data['stemming'].apply(feedbackHasils.getSubjectivity)
        data['afinn'] = data['stemming'].apply(feedbackHasils.getAfinnScore)

        # Standarisasi data
        scaler = StandardScaler()
        data_selected = data[['polarity', 'subjectivity', 'afinn']]
        data_scaled = scaler.fit_transform(data_selected)

        best_eps, best_min_samples, best_score = feedbackHasils.chekEpsMinRadius(data_scaled)

        # Menentukan parameter DBSCAN
        eps = best_eps  
        min_samples = best_min_samples

        session['silhouette_score'] = best_score

        # Membuat model DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')

        # Melakukan clustering
        clusters = dbscan.fit_predict(data_scaled)

        # Menambahkan kolom cluster ke DataFrame
        data['cluster'] = clusters
        
        data['sentiment'] = data['cluster'].apply(feedbackHasils.get_sentiment_label)

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = created_at
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM kluster WHERE user_id=%s""", (session['user_id'],))
        for index, row in data.iterrows():
            cur.execute("INSERT INTO kluster (kluster,feedback, user_id, feedback_id, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (
                            row['sentiment'], 
                            row['text'], 
                            session['user_id'], 
                            row['id'], 
                            created_at,
                            updated_at
                            ))
        mysql.connection.commit()
        cur.close()

        flash('Data Berhasil Di Kluster', 'success')
        return redirect(url_for('feedback_hasil_routes.postFeedbackHasil'))

@feedback_hasil_routes.route('/dashboard/feedback/hasil/export_excel')
def export_excel():
    try:
        feedback_data = feedbackHasils.get_feedback_kluster_from_database(session['user_id'])
        
        df = pd.DataFrame(feedback_data, columns=['kluster', 'feedback', 'feedback_name', 'jalur_pembelajaran', 'sesi', 'program_name', 'batch_name'])

        df.insert(0, 'no_urut', range(1, len(df) + 1))

        ordered_columns = ['no_urut', 'feedback_name', 'jalur_pembelajaran', 'program_name', 'batch_name', 'sesi', 'feedback', 'kluster']
        df = df[ordered_columns]

        df.columns = ['No Urut', 'Name', 'Jalur Pembelajaran', 'Progra Name', 'Batch', 'Sesi', 'Feedback', 'Sentiment']
        
        wb = Workbook()
        ws = wb.active

        header_font = Font(name='Times New Roman', size=12, bold=True)
        header_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        for col_num, column_title in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_num, value=column_title)
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.fill = header_fill

        data_font = Font(name='Times New Roman', size=12)
        for row_num, row_data in enumerate(df.values, 2):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=cell_value)
                cell.font = data_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

        ws.column_dimensions['A'].width = 10  
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 50
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 50
        ws.column_dimensions['H'].width = 50

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            ws.row_dimensions[row[0].row].height = 70

        wrap_columns = ['G']
        for col in wrap_columns:
            for cell in ws[col]:
                cell.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')

        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        return send_file(excel_file, download_name='feedback_kluster.xlsx', as_attachment=True)
    except:
        flash('Excel Gagal Dicetak', 'danger')
        return redirect(url_for('feedback_hasil_routes.postFeedbackHasil'))
    