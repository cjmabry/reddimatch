import ConfigParser, os
config = ConfigParser.ConfigParser()
config.read('./oauth_config.ini')
config.set('app','app_key',os.environ['REDDIT_NOTIFIER_ID'])
config.set('app','app_secret',os.environ['REDDIT_NOTIFIER_SECRET'])

with open(r'./oauth_config.ini', 'wb') as configfile:
    config.write(configfile)
