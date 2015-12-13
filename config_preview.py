DEBUG = False
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROPAGATE_EXCEPTIONS = False

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
DATABASE_CONNECT_OPTIONS = {}

REDDIT_USER_AGENT = 'web:com.reddimatch:v0.9.0 (by /u/cjmabry)'
REDDIT_CLIENT_ID = 'R6NOkcOGXv1xUw'
REDDIT_CLIENT_SECRET = '73pZJK5-lOxf5jRiW6YqJ-IMPgg'
REDDIT_REDIRECT_URI = 'http://45.55.207.88/authorize_callback'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'

THREADS_PER_PAGE = 2

SECRET_KEY = 'secret'

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['cjmab28@gmail.com']
