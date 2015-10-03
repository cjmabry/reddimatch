import app, time
from pprint import pprint
from app import reddit_api, db, models

user = models.User.query.filter_by(username='cjmabry').first()

# time1 = time.time()
# subs = reddit_api.get_favorite_subs_2(user)
# time2 = time.time()
#
# print(time2 - time1)
# print subs

favs = user.favorited_subs().all()

reddit_api.get_offsite_users(favs)
