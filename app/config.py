import os
import dotenv

dotenv.load_dotenv('.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('API_KEY'),
        "authDomain": os.getenv('AUTH_DOMAIN'),
        "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
        "projectId": os.getenv('PROJECT_ID'),
        "storageBucket": os.getenv('STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('MESSAGING_SENDER_ID'),
        "appId": os.getenv('APP_ID'),
        "measurementId": os.getenv('MEASUREMENT_ID')
    }
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    FIREBASE_ADMIN_SDK_PATH = os.getenv('ADMIN_SDK_PATH')