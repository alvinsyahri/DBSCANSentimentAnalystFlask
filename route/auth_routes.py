from flask import Blueprint, render_template, request, redirect, session, make_response, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

# COOKIE_TIME_OUT = 60*60*24*7 #7 days
COOKIE_TIME_OUT = 60*5 #5 minutes

auth_routes = Blueprint('auth_routes', __name__)
mysql = MySQL()
bcrypt = Bcrypt()

@auth_routes.route('/login', methods = ['GET'])
def getLogin():
    return render_template('page/auth-login-basic.html')


@auth_routes.route('/login', methods=['POST'])
def postLogin():
    username = request.form['username']
    password = request.form['password']
    remember = request.form.getlist('remember')
  
    if 'uname' in request.cookies:
        username = request.cookies.get('uname')
        password = request.cookies.get('pwd')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, username, password, role FROM user WHERE username=%s", (username,))
        row = cur.fetchone()
        mysql.connection.commit()
        if row and bcrypt.check_password_hash(row[3], password):
            session['id'] = row[0]
            session['name'] = row[1]
            session['username'] = row[2]
            session['role'] = row[4]
            cur.close()
            return redirect('/dashboard')
        else:
            flash('Username atau Password Anda Salah', 'danger')
            return redirect('/login')
    # validate the received values
    elif username and password:
        #check user exists   
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, username, password, role FROM user WHERE username=%s", (username,))
        row = cur.fetchone()
        mysql.connection.commit()
        if row:
            if bcrypt.check_password_hash(row[3], password):
                session['user_id'] = row[0]
                session['name'] = row[1]
                session['username'] = row[2]
                session['role'] = row[4]
                cur.close()
                if remember:
                    resp = make_response(redirect('/dashboard'))
                    resp.set_cookie('uname', row[2], max_age=COOKIE_TIME_OUT)
                    resp.set_cookie('pwd', password, max_age=COOKIE_TIME_OUT)
                    resp.set_cookie('rem', 'checked', max_age=COOKIE_TIME_OUT)
                    return resp
                return redirect('/dashboard')
            else:
                flash('Username atau Password Anda Salah', 'danger')
                return redirect('/login')
        else:
            flash('Username atau Password Anda Salah', 'danger')
            return redirect('/login')
    else:
        flash('Username atau Password Anda Salah', 'danger')
        return redirect('/login')
   
@auth_routes.route('/logout')
def logout():
    if 'username' in session:
        session.pop('name', None)
        session.pop('username', None)
        session.pop('role', None)
        session.pop('category_choice', None)
        session.pop('plot', None)
    return redirect('/login')

@auth_routes.route('/cookie')
def cookiees():
    if 'rem' in request.cookies:
        resp = make_response('Cookie dihapus!')
        resp.set_cookie('uname', value='', expires=0)
        resp.set_cookie('pwd', value='', expires=0)
        resp.set_cookie('rem', value='', expires=0)
        return resp
    return redirect('/login')

