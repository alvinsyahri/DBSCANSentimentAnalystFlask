from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import MySQLdb
from flask_mysqldb import MySQL

program_routes = Blueprint('program_routes', __name__)
mysql = MySQL()

@program_routes.route('/dashboard/program', methods = ['GET'])
def getProgram():
    if 'username' in session and session['role'] == 0:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, path FROM program ORDER BY createdAt DESC")
        program = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('page/program.html', programs=program, title='Program')
    elif 'username' in session and session['role'] == 1:
        return render_template('page/pages-misc-error.html')
    else:
        return redirect('/login')

@program_routes.route('/dashboard/program', methods = ['POST'])
def postProgram():
    if 'username' in session and session['role'] == 0:
        try:
            name = request.form['name']
            path = int(request.form['path'])
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = created_at

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO program (name, path, createdAt, updatedAt) VALUES (%s, %s, %s, %s)", (name, path, created_at, updated_at))
            
            mysql.connection.commit()
            cur.close()
            print([name, path])

            flash('Program Baru Berhasil Ditambahkan', 'success')
            return redirect(url_for('program_routes.getProgram'))
        except MySQLdb.IntegrityError as e:
            flash('Program Baru Gagal Ditambahkan Data Program Sudah Ada', 'danger')
            return redirect(url_for('program_routes.getProgram'))
        except Exception as e:
            flash(f'Program Gagal Ditambahkan', 'danger')
            return redirect(url_for('program_routes.getProgram'))
    else:
        return render_template('page/pages-misc-error.html')

@program_routes.route('/dashboard/program/<program_id>', methods=['POST', 'PUT', 'DELETE'])
def putAndDeleteProgram(program_id):
    if 'username' in session and session['role'] == 0:
        if(request.form['_method'] == 'PUT'):
            try:
                name = request.form['name']
                path = request.form['path']
                updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cur = mysql.connection.cursor()
                cur.execute("""UPDATE program set name=%s, path=%s, updatedAt=%s WHERE id=%s""", (name, path, updated_at, program_id))
                
                mysql.connection.commit()
                cur.close()

                flash('Program Berhasil Dirubah', 'success')
                return redirect(url_for('program_routes.getProgram'))
            except MySQLdb.IntegrityError as e:
                flash('Program Gagal Dirubah Data Program Sudah Ada', 'danger')
                return redirect(url_for('program_routes.getProgram'))
            except:
                flash('Program Gagal Dirubah', 'danger')
                return redirect(url_for('program_routes.getProgram'))
        elif(request.form['_method'] == 'DELETE'):
            try:
                cur = mysql.connection.cursor()
                cur.execute("""DELETE FROM program WHERE id=%s""", (program_id,))
                
                mysql.connection.commit()
                cur.close()

                flash('Program Berhasil Dihapus', 'success')
                return redirect(url_for('program_routes.getProgram'))
            except:
                flash('Program Gagal Dihapus', 'danger')
                return redirect(url_for('program_routes.getProgram'))
    else:
        return render_template('page/pages-misc-error.html')