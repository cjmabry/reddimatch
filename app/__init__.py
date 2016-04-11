from flask import Flask, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.images import Images
from flask_socketio import SocketIO
from werkzeug.contrib.fixers import ProxyFix
import os, sys
from flask.ext.mail import Mail
import logging, time, datetime

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)
images = Images(app)

mail = Mail(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

socketio = SocketIO(app)

db = SQLAlchemy(app)

if app.debug:
    app.logger.setLevel(logging.INFO)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler, SMTPHandler
    file_handler = RotatingFileHandler('tmp/reddimatch.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('reddimatch startup')

    # credentials = None
    # if MAIL_USERNAME or MAIL_PASSWORD:
    #     credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    # mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), MAIL_USERNAME, ADMINS, 'reddimatch failure', credentials)
    # mail_handler.setLevel(logging.ERROR)
    # app.logger.addHandler(mail_handler)

from app import views, models
