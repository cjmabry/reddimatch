from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
message = Table('message', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('content', Text),
    Column('to_id', Integer),
    Column('from_id', Integer),
    Column('time_sent', DateTime),
    Column('match_type', String(length=10)),
    Column('read', Boolean),
    Column('deleted', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['message'].columns['deleted'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['message'].columns['deleted'].drop()
