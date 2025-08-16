import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-fallback-secret-key-that-is-very-long')
    DATABASE = os.environ.get('DATABASE_URL', 'content.db')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
