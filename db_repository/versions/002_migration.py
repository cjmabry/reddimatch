from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
match_table = Table('match_table', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_from_id', Integer),
    Column('user_to_id', Integer),
    Column('match_type', String(length=10)),
    Column('matched_on', DateTime),
    Column('accepted', Boolean),
    Column('rejected', Boolean),
    Column('deleted', Boolean),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['match_table'].columns['deleted'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['match_table'].columns['deleted'].drop()
