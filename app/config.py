import os
import dotenv

dotenv.load_dotenv('.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('API_KEY'),
        "authDomain": os.getenv('AUTH_DOMAIN'),
        "databaseURL": os.getenv('DATABASE_URL'),
        "projectId": os.getenv('PROJECT_ID'),
        "storageBucket": os.getenv('STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('MESSAGING_SENDER_ID'),
        "appId": os.getenv('APP_ID'),
        "measurementId": os.getenv('MEASUREMENT_ID')
    }
    FIREBASE_ADMIN_SDK_PATH = os.getenv('ADMIN_SDK_PATH')