from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    refresh_token = db.Column(db.String(60))
    age = db.Column(db.Integer)
    postal_code = db.Column(db.String(10))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    bio = db.Column(db.String(140))
    profile_photo_url = db.Column(db.String(120))
    favorited = db.relationship('User', secondary=favorite_subs, primaryjoin = (favorite_subs.c.user_id == id), secondaryjoin=(favorite_subs.c.))
    # last_updated = db.Column(db.)
    # created

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.username

#TODO table for favorite subs

class Subreddit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    

favorite_subs = db.Table('favorite_subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subreddit', db.String(60))
)
