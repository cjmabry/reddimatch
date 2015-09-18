from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
favorite_subs = Table('favorite_subs', post_meta,
    Column('user_id', Integer),
    Column('subreddit_id', Integer),
)

subreddit = Table('subreddit', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('reddit_id', Integer),
    Column('name', String(length=60)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['favorite_subs'].create()
    post_meta.tables['subreddit'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['favorite_subs'].drop()
    post_meta.tables['subreddit'].drop()
