from flask import Blueprint, json, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, current_user, logout_user
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials, firestore
from app.auth.forms import LoginForm, RegistrationForm
from app.models.user import User, db
from app.config import Config
import os
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    print('Route accessed')  
    form = LoginForm()
    print('Form created')  
    
    if request.method == 'POST':
        print('POST request received')  
        print('Form data:', form.data)  
    else:
        print('GET request received')
    
    print('Form errors:', form.errors)

    if form.validate_on_submit():
        print('Form submitted successfully!')  
        email = form.email.data
        password = form.password.data
        try:
            firebase_user = firebase_admin.auth.get_user_by_email(email)
            
            auth = Config.firebase.auth()
            user_auth = auth.sign_in_with_email_and_password(email, password)
            print('Firebase user found and authenticated:', email)

            # Check if user exists in our database
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    id_=firebase_user.uid,
                    name=firebase_user.display_name or email.split('@')[0],
                    email=email,
                    profile_pic=firebase_user.photo_url or ""
                )
                db.session.add(user)
                db.session.commit()

            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            print('Error during login:', str(e))  
            form.password.errors = ["Invalid email or password. Please try again."]

    print('Form not submitted')  
    return render_template('login.html', form=form, config=Config)

@auth_bp.route('/handle_firebase_auth', methods=['POST'])
def handle_firebase_auth():
    try:
        # Get the ID token from the request
        id_token = request.json.get('idToken')
        if not id_token:
            return json.jsonify({'error': 'No ID token provided'}), 400
        
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Get the user's info from Firebase
        user_record = firebase_auth.get_user(uid)
        email = user_record.email
        
        # First check if a user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Handle the case where the email already exists but with a different ID
            if existing_user.id != uid:
                # Link the accounts - update the existing user with the new UID
                existing_user.id = uid
                # Update other fields if needed
                existing_user.name = user_record.display_name
                existing_user.profile_pic = user_record.photo_url or ""
                db.session.commit()
                user = existing_user
            else:
                user = existing_user
        else:
        # Check if user exists in our database
            user = User.query.filter_by(id=uid).first()
            if not user:
                # Create a new user in database
                user = User(
                    id_=uid,
                    name=user_record.display_name,
                    email=user_record.email,
                    profile_pic=user_record.photo_url or ""
                )
                db.session.add(user)
                db.session.commit()
                
                # Create user in Firestore
                firestore_db = firestore.client()
                firestore_db.collection('users').document(uid).set({
                    'name': user_record.display_name,
                    'email': user_record.email,
                    'profile_pic': user_record.photo_url or "",
                    'created_at': datetime.now(),
                    'last_login': datetime.now(),
                    'auth_provider': 'google'
                })
            else:
                # Update last login time
                firestore_db = firestore.client()
                firestore_db.collection('users').document(uid).update({
                    'last_login': datetime.now()
                })
        
        # Log in the user
        login_user(user)
        
        return json.jsonify({'success': True}), 200
    
    except Exception as e:
        return json.jsonify({'error': str(e)}), 400

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
        
    form = RegistrationForm()
    print("Form data: 1") 
    if form.validate_on_submit():
        print("Form data: 2")  
        email = form.email.data
        password = form.password.data
        username = form.name.data if hasattr(form, 'name') else email.split('@')[0]
        
        try:
            # Create user in Firebase Auth
            user_record = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            # Create user in database
            user = User(
                id_=user_record.uid,
                name=username,
                email=email,
                profile_pic=""
            )
            db.session.add(user)
            db.session.commit()
            
            # Create user in Firestore
            firestore_db = firestore.client()
            firestore_db.collection('users').document(user_record.uid).set({
                'name': username,
                'email': email,
                'profile_pic': "",
                'created_at': datetime.now(),
                'last_login': None,
                'auth_provider': 'email'
            })
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

# Helper function to get user data from Firestore
def get_user_from_firestore(user_id):
    try:
        firestore_db = firestore.client()
        user_doc = firestore_db.collection('users').document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        print(f"Error retrieving user from Firestore: {e}")
        return None