#!/bin/bash
# start nginx
sudo service nginx start

# run app
sudo nginx -s reload

# db migration
cd /home/www/reddimatch
source venv/bin/activate
python db_upgrade.py

source venv/bin/activate
gunicorn --worker-class eventlet wsgi -b 0.0.0.0:8000 -D -p /home/www/reddimatch/tmp/gunicorn.pid
