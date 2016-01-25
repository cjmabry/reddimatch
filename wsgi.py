#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)

from app import app as application, socketio

if __name__ == '__main__':
    socketio.run(app)
