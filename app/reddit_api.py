import praw, operator
from flask import url_for, g
from app import db, models
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from config import REDDIT_USER_AGENT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI

def praw_instance():
    r = praw.Reddit(REDDIT_USER_AGENT)

    r.set_oauth_app_info(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, redirect_uri=REDDIT_REDIRECT_URI)

    return r

def generate_url(state, scope, refreshable):
    r = praw.Reddit(REDDIT_USER_AGENT)

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
        url = url_for('dashboard')
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
    db.session.commit()
    login_user(user)

@login_required
def get_favorite_subs():
    r = praw_instance()
    username = g.user.username
    user = r.get_redditor(username)
    gen = user.get_submitted(limit=None)

    karma_by_subreddit = {}
    for thing in gen:
        subreddit = thing.subreddit.display_name
        karma_by_subreddit[subreddit] = thing.score

    sorted_tuple = sorted(karma_by_subreddit.items(), key=operator.itemgetter(1), reverse=True)

    top_three = sorted_tuple[:3]

    for tup in top_three:
        subreddit_name = str(tup[0])
        if models.Subreddit.query.filter_by(name=subreddit_name).first():
            sub = models.Subreddit.query.filter_by(name=subreddit_name).first()
        else:
            sub = models.Subreddit(name=subreddit_name)
            db.session.add(sub)
            db.session.commit()

        if not g.user.has_favorite(sub):
            fav = g.user.favorite(sub)
            db.session.add(fav)
            db.session.commit

    return top_three
