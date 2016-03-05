DEBUG = False
TESTING = False
PRODUCTION = True
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROPAGATE_EXCEPTIONS = False

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
DATABASE_CONNECT_OPTIONS = {}

CSRF_ENABLED = True

REDDIT_USER_AGENT = os.environ['REDDIMATCH_USER_AGENT']
REDDIT_CLIENT_ID = os.environ['REDDIMATCH_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIMATCH_CLIENT_SECRET']
REDDIT_REDIRECT_URI = os.environ['REDDIMATCH_REDIRECT_URI']

CSRF_SESSION_KEY = os.environ['REDDIMATCH_CSRF_KEY']
SECRET_KEY = os.environ['REDDIMATCH_SECRET_KEY']
REDDIT_STATE = os.environ['REDDIMATCH_STATE']

ADS_ENABLED = True
NOTIFICATIONS_ENABLED = True
