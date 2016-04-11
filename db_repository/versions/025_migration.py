from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('username', VARCHAR(length=80)),
    Column('reddit_username', VARCHAR(length=80)),
    Column('email', VARCHAR(length=255)),
    Column('refresh_token', VARCHAR(length=60)),
    Column('age', INTEGER),
    Column('gender_id', INTEGER),
    Column('desired_gender_id', INTEGER),
    Column('orientation', VARCHAR(length=60)),
    Column('location', VARCHAR(length=120)),
    Column('postal_code', VARCHAR(length=10)),
    Column('latitude', FLOAT),
    Column('longitude', FLOAT),
    Column('bio', VARCHAR(length=140)),
    Column('profile_photo_url', VARCHAR(length=120)),
    Column('registered', BOOLEAN),
    Column('email_verified', BOOLEAN),
    Column('created_on', DATETIME),
    Column('verified_on', DATETIME),
    Column('last_online', DATETIME),
    Column('is_online', BOOLEAN),
    Column('newsletter', BOOLEAN),
    Column('date_searchable', BOOLEAN),
    Column('min_age', INTEGER),
    Column('max_age', INTEGER),
    Column('search_radius', INTEGER),
    Column('oauth_denied', BOOLEAN),
    Column('allow_reddit_notifications', BOOLEAN),
    Column('deleted', BOOLEAN),
    Column('disable_location', BOOLEAN),
    Column('profile_photo_id', VARCHAR(length=120)),
    Column('show_top_comment', BOOLEAN),
    Column('top_comment', VARCHAR),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['bio'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['bio'].create()
