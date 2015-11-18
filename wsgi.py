#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
# sys.path.insert(0,"/var/www/reddimatch/")
# activate_this = '/var/www/reddimatch/venv/bin/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))

from app import app as application, socketio

if __name__ == '__main__':
    socketio.run(app)
