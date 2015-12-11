import praw, operator, collections, time, random, sys, os
from praw.handlers import MultiprocessHandler
from flask import url_for, g
from app import db, models
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from pprint import pprint
from collections import OrderedDict
from config import REDDIT_USER_AGENT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI

handler = MultiprocessHandler()

#TODO try/catch all HTTP and NotFound Errors

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


    print code
    access_information = r.get_access_information(code)
    r.set_access_credentials(**access_information)
    refresh_token = access_information['refresh_token']

    username = get_username(r)

    if models.User.query.filter_by(reddit_username=username).first():
        user = models.User.query.filter_by(reddit_username=username).first()
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

    user = models.User(username=username, reddit_username=username, refresh_token = refresh_token)
    db.session.add(user)
    user.get_reddit_favorite_subs()
    db.session.commit()
    login_user(user)

def get_favorite_subs(user):
    time1 = time.time()
    r = praw_instance()
    # refresh_token = user.refresh_token

    # if refresh_token:
    #     access_information = r.refresh_access_information(refresh_token)
    #     r.set_access_credentials(**access_information)
    #     new_refresh_token = access_information['refresh_token']
    #     user.refresh_token = new_refresh_token
    #     db.session.commit()
    # else:
    #     print('No refresh_token')

    reddit_user = r.get_redditor(user.username)

    comments = reddit_user.get_comments(sort='new', time='all', limit=100)

    comments_by_subreddit = []

    try:
        for comment in comments:
                comments_by_subreddit.append(comment.subreddit.display_name)

    except praw.errors.NotFound as e:
        print e
        print "There be an HTTP error. The user probably doesn't have any comments, or Reddit might be down."

    comments = collections.Counter(comments_by_subreddit)

    top_subs_by_comments = sorted(comments.items(), key=operator.itemgetter(1), reverse=True)

    subs = []

    for key, value in top_subs_by_comments[:3]:
        sub = models.Subreddit(name=key)
        subs.append(sub)

    pprint(comments)
    pprint(subs)

    print(time.time() - time1)
    return subs

def get_offsite_user_favorite_subs(username):
    r = praw_instance()
    reddit_user = r.get_redditor(username)

    comments = reddit_user.get_comments(sort='new', time='all', limit=100)

    comments_by_subreddit = []

    for comment in comments:
        comments_by_subreddit.append(comment.subreddit.display_name)

    comments = collections.Counter(comments_by_subreddit)

    top_subs_by_comments = sorted(comments.items(), key=operator.itemgetter(1), reverse=True)

    subs = []

    for key, value in top_subs_by_comments[:3]:
        sub = models.Subreddit(name=key)
        subs.append(sub)

    return subs

def get_offsite_users(favs):
    r = praw_instance()

    users = []

    for sub in favs:
        subreddit = r.get_subreddit(sub.name)
        comments = subreddit.get_comments(limit=100)

        try:
            for comment in comments:
                    if comment.author and comment.author.name not in users:

                        u = models.User(username=comment.author.name)

                        u.status = 'offsite'
                        u.subreddit = subreddit.display_name

                        users.append(u)

        except praw.errors.NotFound as e:
            print e
            print "There be an HTTP error. The user probably doesn't have any comments, or Reddit might be down."

    users = random.sample(users, 3)
    pprint(users)
    return users
