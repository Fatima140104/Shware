from flask import Flask
from app.config import Config
import pyrebase

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.models.user import User

load_dotenv('.env')  # Load environment variables from .env file

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Firebase
    firebase = pyrebase.initialize_app(app.config['FIREBASE_CONFIG'])
    app.firebase_auth = firebase.auth()  # Attach to app
    app.db = firebase.database()           # Attach to app

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)