#!/bin/bash
# start nginx
sudo service nginx start

# db migration
. ~/.profile
cd /home/www/reddimatch
./venv/bin/python db_upgrade.py

# run app
sudo nginx -s reload

. ~/.profile
./venv/bin/gunicorn --worker-class eventlet wsgi -b 0.0.0.0:8000 -p /home/www/reddimatch/tmp/gunicorn.pid
