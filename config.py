import os
from dotenv import load_dotenv

load_dotenv()
print("Loaded SECRET_KEY:", os.getenv('SECRET_KEY'))


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

# Ensure instance directory exists
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

DB_PATH = os.path.join(INSTANCE_DIR, 'dvwa.db')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hard-to-guess-key')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'  # ✅ Fixed Path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
