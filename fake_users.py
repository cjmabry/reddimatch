import app
from app import db, models, reddit_api
import random, string, praw
from random import randint

def generate_string(size=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

# for x in range(0,1000):
def generate_random_user(username):
    return models.User(username=username, reddit_username=username, email=generate_string(randint(5,10))+'@gmail.com',age=randint(5,110),bio=generate_string(randint(5,140)))

def populate_users(numUsers):
    r = reddit_api.praw_instance()
    subreddit = r.get_subreddit('funny')
    posts = subreddit.get_hot()
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

populate_subreddit_db(100)
