from flask import Blueprint,render_template, request, flash, redirect, url_for
from .models import User, Section, Book
from . import db

auth = Blueprint('auth',__name__)

@auth.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')      

        user = User.query.filter_by(user_id=user_id).first()

        if user:
            if user.password == password:
                flash('Logged in successfully!', category = 'success')
                return redirect(f'/{user.id}/dashboard')
            else:
                flash('Incorrect password, try again.', category = 'error')
        else:
            flash('User doesn\'t exist. Please create an account', category = 'error')
            return render_template("sign_up.html")
    return render_template("login.html")

@auth.route('/admin', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        if user_id == 'admin' and password =='admin':
            return redirect("/home")
        else:
            flash('Incorrect login credentials, please try again.', category = 'error')
        
    return render_template("login.html", role = 'admin')
  
@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(user_id = user_id).first()

        if user:
            flash('User already exists.', category = 'error')
        elif password1 != password2:
            flash('Passwords don\'t match. Please try again.', category = 'error')
        else:
            new_user = User(user_id = user_id, firstName = firstName, password = password1)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category = 'success')
            return render_template("login.html")
       
    return render_template("sign_up.html")
 
@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))