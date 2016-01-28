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

    def test_send_match_request(self):
        u1 = User(username="user1")
        u2 = User(username="user2")

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()

        assert u1.matches_sent.count() == 0
        assert u1.matches_received.count() == 0
        assert u2.matches_sent.count() == 0
        assert u2.matches_received.count() == 0
        assert not u1.is_matched(u2)
        assert not u2.is_matched(u1)
        assert not u1.is_matched(u2, 'friend')
        assert not u2.is_matched(u1, 'friend')
        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        assert u1.matches_sent.count() == 1
        assert u1.matches_received.count() == 0
        assert u2.matches_sent.count() == 0
        assert u2.matches_received.count() == 1
        assert not u1.is_matched(u2)
        assert not u2.is_matched(u1)
        assert not u1.is_matched(u2, 'friend')
        assert not u2.is_matched(u1, 'friend')
        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        m = u2.send_match_request(u1, 'date')
        db.session.add(m)
        db.session.commit()

        assert u1.is_matched(u2)

        m = u2.send_match_request(u1, 'date')
        db.session.add(m)
        db.session.commit()

        assert u1.matches_sent.count() == 1
        assert u1.matches_received.count() == 0
        assert u2.matches_sent.count() == 0
        assert u2.matches_received.count() == 1
        assert u1.is_matched(u2)
        assert u2.is_matched(u1)
        assert u1.is_matched(u2, 'date')
        assert u2.is_matched(u1, 'date')
        assert not u1.is_matched(u2, 'friend')
        assert not u2.is_matched(u1, 'friend')

    def test_unmatch(self):
        u1 = User(username="user1")
        u2 = User(username="user2")

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        am = u2.accept_match(u1, 'date')
        db.session.add(am)
        db.session.commit()

        assert u1.is_matched(u2)
        assert u2.is_matched(u1)
        assert u1.is_matched(u2, 'date')
        assert u2.is_matched(u1, 'date')
        assert not u1.is_matched(u2, 'friend')
        assert not u2.is_matched(u1, 'friend')

        u1.unmatch(u2, 'date')
        assert not u1.is_matched(u2, 'date')
        assert not u2.is_matched(u1, 'date')

        m = u1.send_match_request(u2, 'friend')
        db.session.add(m)
        db.session.commit()

        u2.unmatch(u1, 'friend')

    def test_is_rejected(self):
        u1 = User(username="user1")
        u2 = User(username="user2")

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()

        assert not u1.is_rejected(u2)
        assert not u2.is_rejected(u1)

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        assert not u1.is_rejected(u2)
        assert not u2.is_rejected(u1)
        assert not u1.is_rejected(u2, 'date')
        assert not u2.is_rejected(u1, 'date')
        assert not u1.is_rejected(u2, 'friend')
        assert not u2.is_rejected(u1, 'friend')

        u1.unmatch(u2, 'date')

        assert u1.is_rejected(u2)
        assert u2.is_rejected(u1)
        assert u1.is_rejected(u2, 'date')
        assert u2.is_rejected(u1, 'date')
        assert not u1.is_rejected(u2, 'friend')
        assert not u2.is_rejected(u1, 'friend')

    def test_get_matches(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()


        m = u1.send_match_request(u3, 'date')
        db.session.add(m)
        db.session.commit()

        m = u1.send_match_request(u4, 'friend')
        db.session.add(m)
        db.session.commit()

        assert u1.get_matches() is None

        m = u2.accept_match(u1, 'date')

        assert len(u1.get_matches()) == 1
        assert len(u2.get_matches()) == 1

        assert len(u1.get_matches('date')) == 1
        assert len(u2.get_matches('date')) == 1

        assert u1.get_matches('friend') is None
        assert u2.get_matches('friend') is None

    def test_pending_matches(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        assert u1.get_pending_matches() is None
        assert u1.get_pending_matches('date') is None
        assert u1.get_pending_matches('friend') is None

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        m = u1.send_match_request(u3, 'date')
        db.session.add(m)
        db.session.commit()

        m = u1.send_match_request(u4, 'friend')
        db.session.add(m)
        db.session.commit()

        assert len(u1.get_pending_matches()) == 3
        assert len(u1.get_pending_matches('date')) == 2
        assert len(u1.get_pending_matches('friend')) == 1

        m = u2.accept_match(u1, 'date')
        assert len(u1.get_pending_matches()) == 2
        assert len(u1.get_pending_matches('date')) == 1
        assert len(u1.get_pending_matches('friend')) == 1

        u1.unmatch(u4, 'friend')
        assert len(u1.get_pending_matches()) == 1
        assert len(u1.get_pending_matches('date')) == 1
        assert u1.get_pending_matches('friend') is None

        assert u4.get_pending_matches() is None

    def test_get_match_requests(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        assert u1.get_match_requests() is None
        assert u2.get_match_requests() is None
        assert u3.get_match_requests() is None
        assert u4.get_match_requests() is None

        m = u1.send_match_request(u2, 'date')
        db.session.add(m)
        db.session.commit()

        m = u1.send_match_request(u3, 'date')
        db.session.add(m)
        db.session.commit()

        m = u1.send_match_request(u4, 'friend')
        db.session.add(m)
        db.session.commit()

        assert u1.get_match_requests() is None
        assert len(u2.get_match_requests()) == 1
        assert len(u3.get_match_requests()) == 1
        assert len(u4.get_match_requests()) == 1

        assert len(u2.get_match_requests('date')) == 1
        assert u2.get_match_requests('friend') is None

        assert len(u3.get_match_requests('date')) == 1
        assert u3.get_match_requests('friend') is None

        assert len(u4.get_match_requests('friend')) == 1
        assert u4.get_match_requests('date') is None

    def test_get_unread_messages(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        m = Message(to=u2, to_id = u2.id, from_id = u1.id, author=u1,content="This is the first message!", read=False)

        db.session.add(m)
        db.session.commit()

        assert u1.get_unread_messages().count() == 0
        assert u2.get_unread_messages().count() == 1

        m = Message(to=u2, to_id = u2.id, from_id = u1.id, author=u1,content="This is the second message!", read=False)

        db.session.add(m)
        db.session.commit()

        m = Message(to=u2, to_id = u2.id, from_id = u1.id, author=u1,content="This is the third message!", read=False)

        db.session.add(m)
        db.session.commit()

        assert u1.get_unread_messages().count() == 0
        assert u2.get_unread_messages().count() == 3

        m.read = True
        db.session.commit()

        assert u1.get_unread_messages().count() == 0
        assert u2.get_unread_messages().count() == 2

    def test_get_notifications(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        assert u1.get_notifications() is None
        assert u2.get_notifications() is None

        m = u1.send_match_request(u2, 'friend')

        db.session.add(m)
        db.session.commit()

        assert u1.get_notifications() is None
        assert len(u2.get_notifications()) == 1

        m = Message(to=u2, to_id = u2.id, from_id = u1.id, author=u1,content="This is the second message!", read=False)

        db.session.add(m)
        db.session.commit()

        assert u1.get_notifications() is None
        assert len(u2.get_notifications()) == 2

        m.read = True
        db.session.commit()

        assert u1.get_notifications() is None
        assert len(u2.get_notifications()) == 1

        m = u2.accept_match(u1, 'friend')

        assert u1.get_notifications() is None
        assert u2.get_notifications() is None

    def test_avatar(self):
        u1 = User(username='chris',email='cjmab28@gmail.com')
        u2 = User(username='jim')

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()

        assert 'gravatar' and 'avatar' and '300' in u1.avatar()
        assert 'gravatar' and 'avatar' and '300' in u2.avatar()
        assert 'gravatar' and 'avatar' and '500' in u1.avatar(500)

    def test_favorite(self):
        u1 = User(username='chris',email='cjmab28@gmail.com')
        u2 = User(username='jim')

        s1 = Subreddit(name='trees')
        s2 = Subreddit(name='nsfw')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(s1)
        db.session.add(s2)

        db.session.commit()

        assert not u1.has_favorite(s1)
        assert u1.favorited_subs().count() == 0

        s = u1.favorite(s1)

        db.session.add(s)
        db.session.commit()

        assert u1.has_favorite(s1)
        assert u1.favorited_subs().count() == 1

        s = u1.favorite(s1)

        assert u1.has_favorite(s1)
        assert u1.favorited_subs().count() == 1

    def test_unfavorite(self):
        u1 = User(username='chris',email='cjmab28@gmail.com')
        u2 = User(username='jim')

        s1 = Subreddit(name='trees')
        s2 = Subreddit(name='nsfw')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(s1)
        db.session.add(s2)

        db.session.commit()

        s = u1.favorite(s1)

        db.session.add(s)
        db.session.commit()

        assert u1.has_favorite(s1)
        assert u1.favorited_subs().count() == 1

        assert not u1.has_favorite(s2)
        s = u1.unfavorite(s2)
        assert not u1.has_favorite(s2)

        s = u1.unfavorite(s1)

        assert not u1.has_favorite(s1)
        assert u1.favorited_subs().count() == 0

        s = u1.favorite(s1)

        db.session.add(s)
        db.session.commit()

        s = u1.favorite(s2)

        db.session.add(s)
        db.session.commit()

        assert u1.has_favorite(s1)
        assert u1.has_favorite(s2)
        assert u1.favorited_subs().count() == 2

        s = u1.unfavorite_all()

        assert not u1.has_favorite(s1)
        assert not u1.has_favorite(s2)
        assert u1.favorited_subs().count() == 0

    def test_favorited_subs_offsite(self):
        u = User(username="cjmabry", reddit_username="cjmabry")
        u2 = User(username="dev_testing", reddit_username='dev_testing')

        subs = u.favorited_subs_offsite()

        subs2 = u2.favorited_subs_offsite()

        assert len(subs) == 3
        assert len(subs2) == 0

    def test_get_reddit_favorite_subs(self):
        u = User(username="cjmabry", reddit_username="cjmabry")
        u2 = User(username="dev_testing", reddit_username='dev_testing')

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        u.get_reddit_favorite_subs()
        u2.get_reddit_favorite_subs()

        assert u.favorited_subs().count() > 1
        assert u2.favorited_subs().count() == 0

    def test_get_favorited_users(self):
        u1 = User(username="user1")
        u2 = User(username="user2")
        u3 = User(username="user3")
        u4 = User(username="user4")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        db.session.commit()

        s1 = Subreddit(name='nfl')
        s2 = Subreddit(name='askreddit')
        s3 = Subreddit(name='pics')
        s4 = Subreddit(name='funny')

        u1.favorite(s1)
        u2.favorite(s1)
        u4.favorite(s1)

        assert s1.favorited_users().count() == 3
        assert s2.favorited_users().count() == 0

        assert u1 and u2 and u4 in s1.favorited_users().all()

        u1.unfavorite_all()

        assert s1.favorited_users().count() == 2
        assert u1 not in s1.favorited_users().all()
        assert u2 and u4 in s1.favorited_users().all()

    def test_index(self):
        r =  self.app.get('/')
        assert 'index_page' in r.data

    def test_active_required(self):
        pass

    def test_authorize():
        pass

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    # print("\n\nCoverage Report:\n")
    # cov.report()
    print("HTML version: " + os.path.join(BASE_DIR, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
