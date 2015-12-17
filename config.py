DEBUG = False
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROPAGATE_EXCEPTIONS = False

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://reddimatch:cjm4441993@reddimatch-staging.ckuiwsflfftp.us-west-2.rds.amazonaws.com:3306/db'

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
DATABASE_CONNECT_OPTIONS = {}

REDDIT_USER_AGENT = 'web:com.reddimatch:v1.0.0 (by /u/cjmabry)'
REDDIT_CLIENT_ID = 'R6NOkcOGXv1xUw'
REDDIT_CLIENT_SECRET = '73pZJK5-lOxf5jRiW6YqJ-IMPgg'
REDDIT_REDIRECT_URI = 'http://reddimatch-staging/authorize_callback'

CSRF_ENABLED = True
CSRF_SESSION_KEY = os.urandom(24)

THREADS_PER_PAGE = 2

SECRET_KEY = os.urandom(24)
