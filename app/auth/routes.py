from flask import Blueprint, json, render_template, redirect, url_for, flash, session, request
from flask_login import login_user
import requests
from oauthlib.oauth2 import WebApplicationClient
from app.auth.forms import LoginForm, RegistrationForm
from app.models.user import User, db
from app.config import Config
from app import create_app
import os

auth_bp = Blueprint('auth', __name__)

client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

# Allow insecure transport for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.google_login.data:
            return redirect(url_for('auth.google_login'))
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

@auth_bp.route('/google_login')
def google_login():
    # Redirect to Google's OAuth 2.0 server
    google_provider_cfg = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/google_login/callback')
def google_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided by Google
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(
            id_=unique_id, name=users_name, email=users_email, profile_pic=picture
        )
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("main.home"))

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