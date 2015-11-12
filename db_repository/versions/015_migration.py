from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=80)),
    Column('reddit_username', String(length=80)),
    Column('email', String(length=120)),
    Column('refresh_token', String(length=60)),
    Column('age', Integer),
    Column('gender', String(length=60)),
    Column('location', String(length=120)),
    Column('postal_code', String(length=10)),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('bio', String(length=140)),
    Column('profile_photo_url', String(length=120)),
    Column('registered', Boolean),
    Column('deleted', Boolean),
    Column('is_online', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['is_online'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['is_online'].drop()
