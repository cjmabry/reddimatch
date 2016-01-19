from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=80)),
    Column('reddit_username', String(length=80)),
    Column('email', String(length=255)),
    Column('refresh_token', String(length=60)),
    Column('age', Integer),
    Column('gender_id', Integer),
    Column('desired_gender_id', Integer),
    Column('orientation', String(length=60)),
    Column('location', String(length=120)),
    Column('postal_code', String(length=10)),
    Column('latitude', Float(precision=10)),
    Column('longitude', Float(precision=10)),
    Column('bio', String(length=140)),
    Column('profile_photo_url', String(length=120)),
    Column('registered', Boolean),
    Column('email_verified', Boolean),
    Column('created_on', DateTime),
    Column('verified_on', DateTime),
    Column('last_online', DateTime),
    Column('is_online', Boolean),
    Column('newsletter', Boolean),
    Column('date_searchable', Boolean),
    Column('min_age', Integer),
    Column('max_age', Integer),
    Column('search_radius', Integer),
    Column('oauth_denied', Boolean),
    Column('allow_reddit_notifications', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['allow_reddit_notifications'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['allow_reddit_notifications'].drop()
