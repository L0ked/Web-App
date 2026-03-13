import os

SECRET_KEY = 'secret-key-lab6'

# SQLite for local dev; replace with MySQL URI for production
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
