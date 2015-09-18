from app import db

favorite_subs = db.Table('favorite_subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subreddit_id', db.Integer, db.ForeignKey('subreddit.id'))
)

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
    registered = db.Column(db.Boolean)
    favorited = db.relationship('Subreddit', secondary=favorite_subs,
        backref=db.backref('favorite_subs', lazy='dynamic'), lazy='dynamic')

    def favorite(self, subreddit):
        if not self.has_favorite(subreddit):
            self.favorited.append(subreddit)
            return self

    def unfavorite(self, subreddit):
        if self.has_favorite(subreddit):
            self.favorited.remove(subreddit)
            return self

    def has_favorite(self, subreddit):
        return self.favorited.filter(favorite_subs.c.subreddit_id == subreddit.id).count() > 0

    def favorited_subs(self):
        return Subreddit.query.join(favorite_subs, (favorite_subs.c.subreddit_id == Subreddit.id)).filter(favorite_subs.c.user_id == self.id)

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

class Subreddit(db.Model):
    __tablename__ = 'subreddit'
    id = db.Column(db.Integer, primary_key=True)
    reddit_id = db.Column(db.Integer)
    name = db.Column(db.String(60))

    def favorited_users(self):
        return User.query.join(favorite_subs, favorite_subs.c.user_id == User.id).filter(favorite_subs.c.subreddit_id == self.id)

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<Subreddit %r>' % self.name
