import praw
from app import db, models
from config import REDDIT_USER_AGENT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI

def generate_url(state, scope, refreshable):
    r = praw.Reddit(REDDIT_USER_AGENT)

    r.set_oauth_app_info(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, redirect_uri=REDDIT_REDIRECT_URI)

    url = r.get_authorize_url('uniqueKey','identity', True)

    return url

def create_user(code):
    r = praw.Reddit(REDDIT_USER_AGENT)

    r.set_oauth_app_info(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, redirect_uri=REDDIT_REDIRECT_URI)
    access_information = r.get_access_information(code)
    r.set_access_credentials(**access_information)

    # get username
    authenticated_user = r.get_me()
    username = str(authenticated_user.name)
    refresh_token = access_information['refresh_token']

    if not models.User.query.filter_by(username=username).first():
        user = models.User(username=username, refresh_token = refresh_token)
        db.session.add(user)
        db.session.commit()
    else:
        user = models.User.query.filter_by(username=username).first()
        user.refresh_token = refresh_token
        db.session.commit()
