import app, csv
from app import db, models
from sqlalchemy import func, or_, and_
from datetime import datetime

def export_subs():
    export_dict = {}

    subs = models.Subreddit.query.all()

    for sub in subs:
        export_dict[sub.name] = sub.favorited_users().count()

    export = open('data/subreddit_favorites_' + str(datetime.now()), 'wb')
    writer = csv.writer(export)
    for key, value in export_dict.items():
        writer.writerow([key,value])
