import app
from app import db
from hashlib import md5
from sqlalchemy import func, or_, and_
from datetime import datetime

favorite_subs = db.Table('favorite_subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subreddit_id', db.Integer, db.ForeignKey('subreddit.id'))
)

class Match(db.Model):
    __tablename__ = 'match_table'
    id = db.Column(db.Integer, primary_key=True)
    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    match_type = db.Column(db.String(10))
    matched_on = db.Column(db.DateTime)
    accepted = db.Column(db.Boolean)
    rejected = db.Column(db.Boolean)
    user_from = db.relationship("User", foreign_keys=[user_from_id])
    user_to = db.relationship("User", foreign_keys=[user_to_id])

    def __repr__(self):
        return '<Match request to %s>' % self.user_to.username

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    reddit_username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(60))
    age = db.Column(db.Integer)
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'))
    desired_gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'))
    gender = db.relationship("Gender", foreign_keys=[gender_id])
    desired_gender = db.relationship("Gender", foreign_keys=[desired_gender_id])
    orientation = db.Column(db.String(60))
    location = db.Column(db.String(120))
    postal_code = db.Column(db.String(10))
    latitude = db.Column(db.Float(10))
    longitude = db.Column(db.Float(10))
    bio = db.Column(db.String(140))
    profile_photo_url = db.Column(db.String(120))
    registered = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean)
    favorited = db.relationship('Subreddit', secondary=favorite_subs,
        backref=db.backref('favorite_subs', lazy='dynamic'), lazy='dynamic')
    registered = db.Column(db.Boolean)
    email_verified = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime)
    verified_on = db.Column(db.DateTime)
    last_online = db.Column(db.DateTime)
    is_online = db.Column(db.Boolean)
    newsletter = db.Column(db.Boolean)
    date_searchable = db.Column(db.Boolean)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    search_radius = db.Column(db.Integer)
    oauth_denied = db.Column(db.Boolean)

    matches_sent = db.relationship('Match', backref='match_sender', primaryjoin=(id==Match.user_from_id),lazy='dynamic')
    matches_received = db.relationship('Match', primaryjoin=(id==Match.user_to_id), backref='match_recipient', lazy='dynamic')

    def send_match_request(self, user, match_type):
        """Send a match request from self to user of type match_type"""
        print self
        print user
        print match_type
        if not self.is_matched(user, match_type) and not self.is_rejected(user, match_type) and not self.has_sent_match(user, match_type):
            print 1
            if self.has_received_match(user, match_type):
                print 2
                self.accept_match(user, match_type)
                return self
            else:
                print 3
                match = Match(user_from_id = self.id, user_to_id = user.id, match_type = match_type, matched_on = datetime.now(), accepted=False, rejected=False)
                db.session.add(match)
                db.session.commit()
                self.matches_sent.append(match)
                user.matches_received.append(match)
                db.session.add(user)
                db.session.commit()
                return self
        print 4
        return self

    def accept_match(self, user, match_type):
        """Accept a match request"""
        print 11
        match = self.matches_received.filter(Match.user_from_id == user.id,Match.match_type==match_type).first()
        match.accepted = True
        match.rejected = False
        match.matched_on = datetime.now()
        db.session.add(match)
        db.session.commit()
        return self

    def is_matched(self, user, match_type = None):
        """Check if self is matched and accepted with user"""
        if match_type:
            if self.has_sent_match(user, match_type):
                if self.matches_sent.filter(Match.user_to_id == user.id, Match.match_type == match_type).first().accepted:
                    return True
            if self.has_received_match(user, match_type):
                if self.matches_received.filter(Match.user_from_id == user.id, Match.match_type == match_type).first().accepted:
                    return True
            else:
                return False
        else:
            if self.has_sent_match(user):
                if self.matches_sent.filter(Match.user_to_id == user.id).first().accepted:
                    return True
            if self.has_received_match(user):
                if self.matches_received.filter(Match.user_from_id == user.id).first().accepted:
                    return True
            else:
                return False

    def has_received_match(self, user, match_type=None):
        """Check if current user has received a match request from user"""
        if match_type:
            print 111
            return self.matches_received.filter(Match.user_from_id == user.id, Match.match_type==match_type).count() > 0
        else:
            print 222
            return self.matches_received.filter(Match.user_from_id == user.id).count() > 0

    def has_sent_match(self, user, match_type=None):
        """Check if current user has sent a match to user"""
        if match_type:
            return self.matches_sent.filter(Match.user_to_id == user.id, Match.match_type==match_type).count() > 0
        else:
            return self.matches_sent.filter(Match.user_to_id == user.id).count() > 0

    def unmatch(self, user, match_type):
        """Unmatch user from the current user and reject them"""
        if self.has_sent_match(user, match_type):
            match = self.matches_sent.filter(Match.user_to_id == user.id, Match.match_type==match_type).first()
            match.rejected = True
            match.accepted = False
            db.session.add(match)
        if self.has_received_match(user, match_type):
            match = self.matches_received.filter(Match.user_from_id == user.id, Match.match_type==match_type).first()
            match.rejected = True
            match.accepted = False
            db.session.add(match)
        else:
            match = Match(user_from_id = self.id, user_to_id = user.id, match_type = match_type, matched_on = datetime.now(), accepted=False, rejected=True)
            db.session.add(match)
            self.matches_sent.append(match)
        db.session.add(self)
        db.session.commit()

    def is_rejected(self, user, match_type=None):
        """ Check if user has been rejected by self """
        if match_type:
            if self.has_sent_match(user, match_type):
                if self.matches_sent.filter(Match.user_to_id == user.id, Match.match_type==match_type).first().rejected == True:
                    return True
            if self.has_received_match(user, match_type):
                if self.matches_received.filter(Match.user_from_id == user.id, Match.match_type==match_type).first().rejected == True:
                    return True
            return False
        else:
            if self.has_sent_match(user):
                if self.matches_sent.filter(Match.user_to_id == user.id).first().rejected == True:
                    return True
            if self.has_received_match(user):
                if self.matches_received.filter(Match.user_from_id == user.id).first().rejected == True:
                    return True
            return False

    # def unreject(self, user, match_type):
    #     """ Unreject user and allow to be matched with again """
    #
    #     # only use this when the user has permission to unreject himself, i.e. if he is the one who rejected the user and wishes to unreject, but not if a user has rejected him
    #
    #     if self.is_rejected(user, match_type):
    #         if self.has_sent_match(user, match_type):
    #             match = self.matches_sent.filter(Match.user_to_id == user.id, Match.match_type==match_type).first()
    #             match.rejected = False
    #             db.session.add(match)
    #         if self.has_received_match(user, match_type):
    #             match = self.matches_received.filter(Match.user_from_id == user.id, Match.match_type==match_type).first()
    #             match.rejected = False
    #             db.session.add(match)
    #         db.session.commit()
    #         return self

    def get_matches(self, match_type=None):
        """Get all of self's matches that have been accepted and haven't been rejected"""
        matches = []

        if match_type:
            if self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == True).count() > 0:
                matches.extend(self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == True))

            if self.matches_received.filter(Match.match_type==match_type, not Match.rejected == False, Match.accepted == True).count() > 0:
                matches.extend(self.matches_received.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == True))
        else:
            if self.matches_sent.filter(Match.rejected == False, Match.accepted == True).count() > 0:
                matches.extend(self.matches_sent.filter(Match.rejected == False, Match.accepted == True))

            if self.matches_received.filter(Match.rejected == False, Match.accepted == True).count() > 0:
                matches.extend(self.matches_received.filter(Match.rejected == False, Match.accepted == True))

        if len(matches) > 0:
            return matches

    def get_pending_matches(self, match_type=None):
        """Get all matches that self has sent that have not been accepted or rejected yet"""
        matches = []

        if match_type:
            if self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == False).count() > 0:
                matches.extend(self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == False))

            # if self.matches_received.filter(Match.match_type==match_type, not Match.rejected == False, Match.accepted == False).count() > 0:
            #     matches.extend(self.matches_received.filter(Match.match_type==match_type, Match.rejected == False, Match.accepted == False))
        else:
            if self.matches_sent.filter(Match.rejected == False, Match.accepted == False).count() > 0:
                matches.extend(self.matches_sent.filter(Match.rejected == False, Match.accepted == False))

            # if self.matches_received.filter(Match.rejected == False, Match.accepted == False).count() > 0:
            #     matches.extend(self.matches_received.filter(Match.rejected == False, Match.accepted == False))

        if len(matches) > 0:
            return matches

    # def get_matches(self, match_type=None):
    #     """Get all of self's matches that haven't been rejected"""
    #     matches = []
    #
    #     if match_type:
    #         if self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False).count() > 0:
    #             matches.extend(self.matches_sent.filter(Match.match_type==match_type, Match.rejected == False))
    #
    #         if self.matches_received.filter(Match.match_type==match_type, not Match.rejected == False).count() > 0:
    #             matches.extend(self.matches_received.filter(Match.match_type==match_type, Match.rejected == False))
    #     else:
    #         if self.matches_sent.filter(Match.rejected == False).count() > 0:
    #             matches.extend(self.matches_sent.filter(Match.rejected == False))
    #
    #         if self.matches_received.filter(Match.rejected == False).count() > 0:
    #             matches.extend(self.matches_received.filter(Match.rejected == False))
    #
    #     if len(matches) > 0:
    #         return matches

    def get_match_requests(self, match_type=None):
        """Get match requests

        Get all users that have matched that haven't been accepted or rejected
        """

        if match_type:
            matches = self.matches_received.filter(Match.match_type == match_type, Match.rejected == False, Match.accepted == False).all()
        else:
            matches = self.matches_received.filter(Match.rejected == False, Match.accepted == False).all()

        if len(matches) > 0:
            return matches

    def avatar(self, size=300):
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
        for sub in subs:
            self.unfavorite(sub)

    def has_favorite(self, subreddit):
        return self.favorited.filter(favorite_subs.c.subreddit_id == subreddit.id).count() > 0

    def favorited_subs(self):
        return Subreddit.query.join(favorite_subs, (favorite_subs.c.subreddit_id == Subreddit.id)).filter(favorite_subs.c.user_id == self.id)

    def favorited_subs_offsite(self):
        return app.reddit_api.get_offsite_user_favorite_subs(self.username)

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

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_active

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
    match_type = db.Column(db.String(10))
    read = db.Column(db.Boolean)

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<Message ID %r>' % self.id

class Gender(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return self.name
