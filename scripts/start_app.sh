#!/bin/bash
# start nginx
sudo service nginx start

# run app
sudo nginx -s reload
cd /home/www/reddimatch
gunicorn --worker-class eventlet wsgi -b 0.0.0.0:8000 -D -p /home/www/reddimatch/tmp/gunicorn.pid
