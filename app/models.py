import app
from app import db
from hashlib import md5
from sqlalchemy import func, or_, and_

# TODO allow user to accept/reject the match before matching

favorite_subs = db.Table('favorite_subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subreddit_id', db.Integer, db.ForeignKey('subreddit.id'))
)

matches = db.Table('matches',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('matched_id', db.Integer, db.ForeignKey('user.id'))
)

rejects = db.Table('rejects',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('rejected_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    reddit_username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(60))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(60))
    orientation = db.Column(db.String(60))
    location = db.Column(db.String(120))
    postal_code = db.Column(db.String(10))
    latitude = db.Column(db.Float(10))
    longitude = db.Column(db.Float(10))
    bio = db.Column(db.String(140))
    profile_photo_url = db.Column(db.String(120))
    registered = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)
    favorited = db.relationship('Subreddit', secondary=favorite_subs,
        backref=db.backref('favorite_subs', lazy='dynamic'), lazy='dynamic')
    matched = db.relationship('User',
                               secondary=matches,
                               primaryjoin=(matches.c.user_id == id),
                               secondaryjoin=(matches.c.matched_id == id),
                               backref=db.backref('matches', lazy='dynamic'),
                               lazy='dynamic')
    rejected = db.relationship('User',
                                secondary=rejects,
                                primaryjoin=(rejects.c.user_id == id),
                                secondaryjoin=(rejects.c.rejected_id == id),
                                backref=db.backref('rejects', lazy='dynamic'),
                                lazy='dynamic')
    registered = db.Column(db.Boolean)
    email_verified = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime)
    verified_on = db.Column(db.DateTime)
    last_online = db.Column(db.DateTime)
    is_online = db.Column(db.Boolean)
    newsletter = db.Column(db.Boolean)


    def avatar(self, size):
        if self.email is not None:
            return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

        else:
            return 'http://www.gravatar.com/avatar/?d=identicon&s=%s' % size

    def favorite(self, subreddit):
        if not self.has_favorite(subreddit):
            self.favorited.append(subreddit)
            return self

    def unfavorite(self, subreddit):
        if self.has_favorite(subreddit):
            self.favorited.remove(subreddit)
            return self

    def unfavorite_all(self):
        subs = self.favorited_subs()

        print subs

        for sub in subs:
            self.unfavorite(sub)

    def has_favorite(self, subreddit):
        return self.favorited.filter(favorite_subs.c.subreddit_id == subreddit.id).count() > 0

    def favorited_subs(self):
        return Subreddit.query.join(favorite_subs, (favorite_subs.c.subreddit_id == Subreddit.id)).filter(favorite_subs.c.user_id == self.id)

    def get_reddit_favorite_subs(self):
        u = self
        subs = app.reddit_api.get_favorite_subs(u)

        for sub in subs:
            if Subreddit.query.filter(func.lower(Subreddit.name) == func.lower(sub.name)).first():
                print(sub.name + ' found')
                subreddit = Subreddit.query.filter(func.lower(Subreddit.name) == func.lower(sub.name)).first()
            else:
                print(sub.name + ' not found')
                subreddit = Subreddit(name=func.lower(sub.name))
                db.session.add(subreddit)
            f = u.favorite(subreddit)
            if f is not None:
                db.session.add(f)

        db.session.commit()

    def match(self, user):
        if not self.is_matched(user):
            self.matched.append(user)
            return self

    def unmatch(self, user):
        if self.is_matched(user):
            self.matched.remove(user)
            return self

    def reject(self, user):
        if not self.is_rejected(user):
            if self.is_matched(user):
                self.unmatch(user)
            if user.is_matched(self):
                user.unmatch(self)

            self.rejected.append(user)
            return self

    def is_rejected(self, user):
        return self.rejected.filter(rejects.c.rejected_id == user.id).count() > 0

    def unreject(self, user):
        if self.is_rejected(user):
            self.rejected.remove(user)
            return self

    def is_matched(self, user):
        """Check if user is matched with another

        """
        return self.matched.filter(matches.c.matched_id == user.id).count() > 0

    def get_matches(self):
        """Get matches

        Get all users that the current user has matched with, who may or may not have matched with the current user
        """

        if User.query.join(matches, (matches.c.matched_id == User.id)).filter(matches.c.user_id == self.id).count() > 0:
            return User.query.join(matches, (matches.c.matched_id == User.id)).filter(matches.c.user_id == self.id)

    def get_match_requests(self):
        """Get match requests

        Get all users that have matched with the user whom the user hasn't matched with yet
        """

        query = User.query.join(matches, (matches.c.user_id == User.id)).filter(matches.c.matched_id == self.id)

        requests = []

        for r in query:
            if not self.is_matched(r):
                requests.append(r)

        if len(requests) > 0:
            return requests
        else:
            return False

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
    reddit_id = db.Column(db.String(60))
    category = db.Column(db.String(60))
    name = db.Column(db.String(60), unique = True)

    def favorited_users(self):
        return User.query.join(favorite_subs, favorite_subs.c.user_id == User.id).filter(favorite_subs.c.subreddit_id == self.id)

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<Subreddit %r>' % self.name

class Message(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to = db.relationship('User', foreign_keys=[to_id], backref='received_messages')
    author = db.relationship('User', foreign_keys=[from_id], backref='sent_messages')
    time_sent = db.Column(db.DateTime)

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<Message ID %r>' % self.id
