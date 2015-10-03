#!flask/bin/python
import os
import unittest

from config import BASE_DIR
from app import app, db
from app.models import User, Subreddit

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

    def test_favorite(self):
        user = User(username='john', email='john@example.com')
        subreddit = Subreddit(reddit_id='123456', name='tennesseetitans')
        db.session.add(user)
        db.session.add(subreddit)
        db.session.commit()
        assert user.unfavorite(subreddit) is None
        f = user.favorite(subreddit)
        db.session.add(f)
        db.session.commit()
        assert user.favorite(subreddit) is None
        assert user.has_favorite(subreddit)
        assert user.favorited.count() == 1
        assert user.favorited.first().name == 'tennesseetitans'
        u = user.unfavorite(subreddit)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert user.favorited.count() == 0
        assert not user.has_favorite(subreddit)

    def test_favorite_subreddits_by_submission(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='bill', email='bill@example.com')
        u3 = User(username='susan', email='susan@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        s1 = Subreddit(name='vinyl')
        s2 = Subreddit(name='TennesseeTitans')
        s3 = Subreddit(name='nfl')
        s4 = Subreddit(name='ncaa')

        db.session.add(s1)
        db.session.add(s2)
        db.session.add(s3)
        db.session.add(s4)

        u1.favorite(s1)
        u1.favorite(s1)
        u1.favorite(s4)
        u2.favorite(s1)
        u2.favorite(s2)
        u2.favorite(s3)
        u2.favorite(s4)
        u3.favorite(s4)
        u4.favorite(s1)
        u4.favorite(s4)

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)

        f1 = u1.favorited_subs().all()
        f2 = u2.favorited_subs().all()
        f3 = u3.favorited_subs().all()
        f4 = u4.favorited_subs().all()

        assert len(f1) == 2
        assert len(f2) == 4
        assert len(f3) == 1
        assert len(f4) == 2
        assert f1 == [s1, s4]
        assert f2 == [s1, s2, s3, s4]
        assert f3 == [s4]
        assert f4 == [s1, s4]

    def test_match(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unmatch(u2) is None
        u = u1.match(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.match(u2) is None
        assert u1.is_matched(u2)
        assert u1.matched.count() == 1
        assert u1.matched.first().username == 'susan'
        assert u2.matches.count() == 1
        assert u2.matches.first().username == 'john'
        u = u1.unmatch(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_matched(u2)
        assert u1.matched.count() == 0
        assert u2.matches.count() == 0

    # def test_avatar(self):
    #     u = User(nickname='john', email='john@example.com')
    #     avatar = u.avatar(128)
    #     expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
    #     assert avatar[0:len(expected)] == expected
    #
    # def test_make_unique_nickname(self):
    #     u = User(nickname='john', email='john@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname = User.make_unique_nickname('john')
    #     assert nickname != 'john'
    #     u = User(nickname=nickname, email='susan@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname2 = User.make_unique_nickname('john')
    #     assert nickname2 != 'john'
    #     assert nickname2 != nickname

if __name__ == '__main__':
    unittest.main()
