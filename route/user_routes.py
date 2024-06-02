from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb
from flask_bcrypt import Bcrypt

user_routes = Blueprint('user_routes', __name__)
mysql = MySQL()
bcrypt = Bcrypt()

@user_routes.route('/dashboard/user', methods = ['GET'])
def getUser():
    if 'username' in session and session['role'] == 1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, username, role FROM user ORDER BY createdAt DESC")
        user = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('page/user.html', users=user, title='User')
    elif 'username' in session and session['role'] == 0:
        return render_template('page/pages-misc-error.html')
    else:
        return redirect('/login')

@user_routes.route('/dashboard/user', methods = ['POST'])
def postUser():
    if 'username' in session and session['role'] == 1:
        try:
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = created_at

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user (name, username, password, role, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s)", (name, username, hashed_password, role, created_at, updated_at))
            
            mysql.connection.commit()
            cur.close()

            flash('User Baru Berhasil Ditambahkan', 'success')
            return redirect(url_for('user_routes.getUser'))
        except MySQLdb.IntegrityError as e:
            flash('User Baru Gagal Ditambahkan Username Sudah Digunakan', 'danger')
            return redirect(url_for('user_routes.getUser'))
        except:
            flash('User Baru Gagal Ditambahkan', 'danger')
            return redirect(url_for('user_routes.getUser'))
    else:
        return render_template('page/pages-misc-error.html')

@user_routes.route('/dashboard/user/<user_id>', methods=['POST', 'PUT', 'DELETE'])
def putAndDeleteUser(user_id):
    if 'username' in session and session['role'] == 1:
        if(request.form['_method'] == 'PUT'):
            try:
                name = request.form['name']
                username = request.form['username']
                role = request.form['role']
                updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cur = mysql.connection.cursor()
                cur.execute("""UPDATE user set name=%s, username=%s, role=%s, updatedAt=%s WHERE id=%s""", (name, username, role, updated_at, user_id))
                
                mysql.connection.commit()
                cur.close()

                flash('User Berhasil Dirubah', 'success')
                return redirect(url_for('user_routes.getUser'))
            except MySQLdb.IntegrityError as e:
                flash('User Gagal Dirubah Username Sudah Digunakan', 'danger')
                return redirect(url_for('user_routes.getUser'))
            except:
                flash('User Gagal Dirubah', 'danger')
                return redirect(url_for('user_routes.getUser'))
        elif(request.form['_method'] == 'DELETE'):
            try:
                cur = mysql.connection.cursor()
                cur.execute("""DELETE FROM user WHERE id=%s""", (user_id))
                
                mysql.connection.commit()
                cur.close()

                flash('User Berhasil Dihapus', 'success')
                return redirect(url_for('user_routes.getUser'))
            except:
                flash('User Berhasil Dihapus', 'danger')
                return redirect(url_for('user_routes.getUser'))
    else:
        return render_template('page/pages-misc-error.html')
    
@user_routes.route('/dashboard/user/reset/<user_id>', methods=['POST', 'PUT'])
def putUserReset(user_id):
    if 'username' in session and session['role'] == 1:
        password = request.form['password']
        password2 = request.form['password2']
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if(password == password2):
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            cur = mysql.connection.cursor()
            cur.execute("""UPDATE user set password=%s, updatedAt=%s WHERE id=%s""", (hashed_password, updated_at, user_id))
            
            mysql.connection.commit()
            cur.close()

            flash('Password User Berhasil Dirubah', 'success')
            return redirect(url_for('user_routes.getUser'))
        else:
            flash('Password User Gagal Dirubah', 'danger')
            return redirect(url_for('user_routes.getUser'))
    else:
        return render_template('page/pages-misc-error.html')