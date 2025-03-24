from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.auth.forms import LoginForm, RegistrationForm
from app import create_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            user = create_app().firebase_auth.sign_in_with_email_and_password(email, password)
            session['user_id'] = user['localId']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            create_app().firebase_auth.create_user_with_email_and_password(email, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except:
            flash('Registration failed. Please try again.', 'danger')
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))