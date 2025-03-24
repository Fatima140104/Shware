from flask import Flask
from app.config import Config
import pyrebase
import os
from dotenv import load_dotenv

load_dotenv('.env')  # Load environment variables from .env file

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Firebase
    firebase = pyrebase.initialize_app(app.config['FIREBASE_CONFIG'])
    app.firebase_auth = firebase.auth()  # Attach to app
    app.db = firebase.database()           # Attach to app

    # Register blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app