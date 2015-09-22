import praw, operator
from praw.handlers import MultiprocessHandler
from flask import url_for, g
from app import db, models
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from config import REDDIT_USER_AGENT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI

handler = MultiprocessHandler()

def praw_instance():
    r = praw.Reddit(user_agent=REDDIT_USER_AGENT, handler=handler)

    r.set_oauth_app_info(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, redirect_uri=REDDIT_REDIRECT_URI)

    return r

def generate_url(state, scope, refreshable):
    r = praw_instance()

    r.set_oauth_app_info(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, redirect_uri=REDDIT_REDIRECT_URI)

    url = r.get_authorize_url(state, scope, refreshable)

    return url

def login_reddit_user(code):
    r = praw_instance()

    access_information = r.get_access_information(code)
    r.set_access_credentials(**access_information)
    refresh_token = access_information['refresh_token']

    username = get_username(r)

    if models.User.query.filter_by(username=username).first():
        user = models.User.query.filter_by(username=username).first()
        login_user(user)
        user.refresh_token = refresh_token
        db.session.commit()
        url = url_for('match')
        return url
    else:
        create_user(username, refresh_token)
        url = url_for('register')
        return url


def get_refresh_token(praw_instance, code):

    access_information = r.get_access_information(code)
    r.set_access_credentials(**access_information)

    refresh_token = access_information['refresh_token']

    return refresh_token

def get_username(praw_instance):
    r = praw_instance

    authenticated_user = r.get_me()
    username = str(authenticated_user.name)

    return username

def create_user(username, refresh_token):

    user = models.User(username=username, refresh_token = refresh_token)
    db.session.add(user)
    user.get_reddit_favorite_subs()
    db.session.commit()
    login_user(user)

#TODO validate security
def get_favorite_subs(username):
    r = praw_instance()
    user = r.get_redditor(username)
    gen = user.get_submitted(limit=None)

    karma_by_subreddit = []

    for thing in gen:
        lis = [thing.subreddit.display_name, thing.score]
        karma_by_subreddit.append(lis)

    sorted_list = sorted(karma_by_subreddit, key=operator.itemgetter(1), reverse=True)

    top_three = []

    for lis in sorted_list[:3]:
        subreddit_name = str(lis[0])
        sub = r.get_subreddit(subreddit_name)
        sub = models.Subreddit(name=subreddit_name)
        top_three.append(sub)

    return top_three
