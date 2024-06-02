from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import MySQLdb
from flask_mysqldb import MySQL

batch_routes = Blueprint('batch_routes', __name__)
mysql = MySQL()

@batch_routes.route('/dashboard/batch', methods = ['GET'])
def getBatch():
    if 'username' in session and session['role'] == 0:
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
        batch = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('page/batch.html', batchs=batch, title='Batch')
    elif 'username' in session and session['role'] == 1:
        return render_template('page/pages-misc-error.html')
    else:
        return redirect('/login')
        

@batch_routes.route('/dashboard/batch', methods = ['POST'])
def postBatch():
    if 'username' in session and session['role'] == 0:
        try:
            name = request.form['name']
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = created_at


            # Hilangkan awalan "Batch" atau "batch" jika ada
            name = name.removeprefix("Batch").removeprefix("batch").lstrip()

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO batch (name, createdAt, updatedAt) VALUES (%s, %s, %s)", (name, created_at, updated_at))
            
            mysql.connection.commit()
            cur.close()

            flash('Batch Baru Berhasil Ditambahkan', 'success')
            return redirect(url_for('batch_routes.getBatch'))
        except MySQLdb.IntegrityError as e:
            flash('Batch Baru Gagal Ditambahkan Data Batch Sudah Ada', 'danger')
            return redirect(url_for('batch_routes.getBatch'))
        except:
            flash('Batch Baru Gagal Ditambahkan', 'danger')
            return redirect(url_for('batch_routes.getBatch'))
    else:
        return render_template('page/pages-misc-error.html')
        


@batch_routes.route('/dashboard/batch/<batch_id>', methods=['POST', 'PUT', 'DELETE'])
def putAndDeleteBatch(batch_id):
    if 'username' in session and session['role'] == 0:
        if(request.form['_method'] == 'PUT'):
            try:
                name = request.form['name']
                updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cur = mysql.connection.cursor()
                cur.execute("""UPDATE batch set name=%s, updatedAt=%s WHERE id=%s""", (name, updated_at, batch_id))
                
                mysql.connection.commit()
                cur.close()

                flash('Batch Berhasil Dirubah', 'success')
                return redirect(url_for('batch_routes.getBatch'))
            except MySQLdb.IntegrityError as e:
                flash('Batch Gagal Dirubah Data Batch Sudah Ada', 'danger')
                return redirect(url_for('batch_routes.getBatch'))
            except:
                flash('Batch Gagal Dirubah', 'danger')
                return redirect(url_for('batch_routes.getBatch'))
            
        elif(request.form['_method'] == 'DELETE'):
            try:
                cur = mysql.connection.cursor()
                cur.execute("""DELETE FROM batch WHERE id=%s""", (batch_id,))
                
                mysql.connection.commit()
                cur.close()

                flash('Batch Berhasil Dihapus', 'success')
                return redirect(url_for('batch_routes.getBatch'))
            except:
                flash('Batch Gagal Dihapus', 'danger')
                return redirect(url_for('batch_routes.getBatch'))
    else:
        return render_template('page/pages-misc-error.html')
