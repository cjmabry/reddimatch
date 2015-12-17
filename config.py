DEBUG = True
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROPAGATE_EXCEPTIONS = False

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://reddimatch:cjm4441993@reddimatch.ckuiwsflfftp.us-west-2.rds.amazonaws.com:3306/main'

# if os.environ.get('DATABASE_URL') is None:
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# else:
#     SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
DATABASE_CONNECT_OPTIONS = {}

REDDIT_USER_AGENT = 'web:com.reddimatch:v0.9.0 (by /u/cjmabry)'
REDDIT_CLIENT_ID = 'Q9TKty4V9mQQlA'
REDDIT_CLIENT_SECRET = '1O14gtnAlNy_0X6j5F8E3HDSp9Q'
REDDIT_REDIRECT_URI = 'http://127.0.0.1:8000/authorize_callback'

CSRF_ENABLED = True
CSRF_SESSION_KEY = os.urandom(24)
THREADS_PER_PAGE = 2

SECRET_KEY = 'secret'

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['cjmab28+reddimatch+error@gmail.com']
