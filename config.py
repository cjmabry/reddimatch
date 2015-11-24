DEBUG = True
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROPAGATE_EXCEPTIONS = False

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
DATABASE_CONNECT_OPTIONS = {}

REDDIT_USER_AGENT = 'web:com.reddimatch:v0.8.0 (by /u/cjmabry)'
REDDIT_CLIENT_ID = 'Q9TKty4V9mQQlA'
REDDIT_CLIENT_SECRET = '1O14gtnAlNy_0X6j5F8E3HDSp9Q'
REDDIT_REDIRECT_URI = 'http://127.0.0.1:8000/authorize_callback'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'

THREADS_PER_PAGE = 2

SECRET_KEY = 'secret'
