import app
from app import db, models, reddit_api
import random, string, praw
from random import randint
from loremipsum import get_sentence
import datetime
import math

def generate_string(size=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

# for x in range(0,1000):
def generate_random_user(username):

    bio = get_sentence()[:139]

    coords = generate_random_coordinates(36.1557611, -85.5329124, 160934)

    return models.User(username=username, reddit_username=username, email=generate_string(randint(5,10))+'@gmail.com',age=randint(18,45),bio=bio, registered = True, newsletter=True, latitude = coords[0], longitude=coords[1], email_verified=False,created_on = datetime.datetime.now(), last_online=datetime.datetime.now(), is_online=False, gender_id=randint(1,3), date_searchable=randint(0,1));


def generate_random_coordinates(lat, longitude, radius):
    radiusInDegrees = radius/111300

    r = radiusInDegrees

    x0 = lat
    y0 = longitude

    u = float(random.uniform(0.0,1.0))
    v = float(random.uniform(0.0,1.0))

    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)

    lat  = x + x0
    longitude = y + y0

    location = (lat, longitude)

    return location

def populate_users(numUsers):
    r = reddit_api.praw_instance()
    subreddit = r.get_subreddit('test')
    posts = subreddit.get_hot(limit=numUsers)
    # subreddit = r.get_front_page()

    posts_dict = {}
    for thing in posts:
        username = str(thing.author)

        if not models.User.query.filter_by(reddit_username=username).first():
            u = generate_random_user(username)
            db.session.add(u)
            subs = reddit_api.get_offsite_user_favorite_subs(username)

            for sub in subs:
                if models.Subreddit.query.filter_by(name=sub.name).first():
                    print(sub.name + 'found')
                    subreddit = models.Subreddit.query.filter_by(name=sub.name).first()
                else:
                    print(sub.name + ' not found')
                    subreddit = models.Subreddit(name=sub.name)
                    db.session.add(subreddit)
                f = u.favorite(subreddit)
                if f is not None:
                    db.session.add(f)
                    print('favorited ' + sub.name)
                else:
                    print(sub.name + ' already favorited by ' + str(u))

            db.session.commit()

def populate_subreddit_db(numSubreddits):
    r = reddit_api.praw_instance()
    front_page = r.get_front_page(limit=numSubreddits)

    front_page_dict = {}
    for thing in front_page:
        subreddit_name = str(thing.subreddit)
        subreddit_id = str(thing.subreddit_id)

        if not models.Subreddit.query.filter_by(name=subreddit_name).first():
            sub = models.Subreddit(name=subreddit_name,reddit_id=subreddit_id)
            db.session.add(sub)
            db.session.commit()
        else:
            sub = models.Subreddit.query.filter_by(name=subreddit_name).first()
            sub.reddit_id = subreddit_id

populate_users(1000)
