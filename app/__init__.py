from flask import Flask, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_socketio import SocketIO
from werkzeug.contrib.fixers import ProxyFix
import os, sys

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

socketio = SocketIO(app)

db = SQLAlchemy(app)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/reddimatch.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('reddimatch startup')

from app import views, models
