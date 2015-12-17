#!flask/bin/python
from coverage import coverage
cov = coverage(branch=True, omit=['venv/*', 'tests.py'])
cov.start()

import os
import unittest

from config import BASE_DIR
from app import app, db
from app.models import User, Subreddit, Match, Message, Gender

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_match(self):
        # test matching
        u1 = User(username='cjmabry')
        u2 = User(username='john')
        u3 = User(username='tim')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        assert not u1.get_matches()
        assert not u1.get_match_requests()
        assert not u1.get_pending_matches()
        assert u1.matches_sent.count() == 0
        assert u1.matches_received.count() == 0

        assert u1.get_pending_matches() is None
        assert u2.get_pending_matches() is None

        assert u1.get_match_requests() is None
        assert u2.get_match_requests() is None

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        print u1.matches_sent.all()

        assert len(u1.get_pending_matches()) == 1
        assert u2.get_pending_matches() is None

        assert u1.get_match_requests() is None
        assert len(u2.get_match_requests()) == 1
        assert u2.get_match_requests()[0].user_from == u1

        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        assert u1.matches_sent.count() == 1
        assert u2.matches_received.count() == 1

        m = u2.send_match_request(u1, 'date')
        db.session.add(m)
        db.session.commit()

        print u2.matches_sent.all()

        assert u1.get_pending_matches() is None
        assert u2.get_pending_matches() is None

        assert u2.is_matched(u1, 'date')
        assert u1.is_matched(u2, 'date')

        assert u1.matches_sent.count() == 1
        assert u2.matches_sent.count() == 0
        assert u2.matches_received.count() == 1
        assert u1.matches_received.count() == 0

        assert len(u1.get_matches()) == 1
        assert len(u2.get_matches()) == 1

    def atest_unmatch(self):
        # test unmatching, rejecting, and unrejecting
        u1 = User(username='bill')
        u2 = User(username='jimbo')
        u3 = User(username='ronald')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        u1.unmatch(u2, 'date')

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        m = u2.send_match_request(u1, 'date')
        db.session.add(m)
        db.session.commit()

        assert u1.is_rejected(u2, 'date')
        assert u2.is_rejected(u1, 'date')
        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        m = u2.send_match_request(u1, 'date')
        db.session.add(m)
        db.session.commit()

        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        u1.unmatch(u2, 'date')

        assert u1.is_rejected(u2, 'date')
        assert u2.is_rejected(u1, 'date')
        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        u2.unmatch(u1, 'date')

        m = u3.send_match_request(u1, 'friend')
        db.session.add(m)
        db.session.commit()

        assert not u1.is_rejected(u3, 'friend')
        assert not u3.is_rejected(u1, 'friend')
        assert not u1.is_matched(u3, 'friend')
        assert not u3.is_matched(u1, 'friend')

        u3.unmatch(u1, 'friend')

        assert not u1.is_matched(u3, 'friend')
        assert not u3.is_matched(u1, 'friend')
        assert u1.is_rejected(u3, 'friend')
        assert u3.is_rejected(u1, 'friend')
        assert not u1.is_rejected(u3, 'date')
        assert not u3.is_rejected(u1, 'date')

        u3.unmatch(u1, 'friend')

        assert u1.is_rejected(u3, 'friend')
        assert u3.is_rejected(u1, 'friend')

        m = u1.send_match_request(u3, 'friend')
        db.session.add(m)
        db.session.commit()

    def atest_avatar(self):
        u1 = User(username='billy_bob')
        u2 = User(username='jimmy', email='poop@butt.com')

        assert u1.avatar(300) is not None
        assert u1.avatar() is not None
        assert u2.avatar(300) is not None
        assert u2.avatar() is not None

    def atest_favorites(self):
        u1 = User(username='billy_bob')
        u2 = User(username='cjmabry', email='poop@butt.com')
        sub = Subreddit(name='trees')
        sub2 = Subreddit(name='poop')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(sub)
        db.session.commit()

        f = u1.favorite(sub)
        db.session.add(f)
        db.session.commit()

        assert u1.favorited_subs().count() == 1
        assert u1.favorited_subs().first() == sub

        # assert u2.favorited_subs_offsite()

        f = u1.favorite(sub2)
        db.session.add(f)
        db.session.commit()

        assert u1.favorited_subs().count() == 2

        uf = u1.unfavorite(sub2)
        db.session.add(uf)
        db.session.commit()

        assert u1.favorited_subs().count() == 1

        f = u1.favorite(sub2)
        db.session.add(f)
        db.session.commit()

        assert u1.favorited_subs().count() == 2

        u1.unfavorite_all()
        db.session.commit()

        assert u1.favorited_subs().count() == 0

        assert sub is not None
        assert u1 is not None

    def test_index(self):
        r =  self.app.get('/')
        assert 'index_page' in r.data

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(BASE_DIR, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
