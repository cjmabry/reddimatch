#!/bin/bash
# set up virtual env
cd /home/www/reddimatch

if [ "$DEPLOYMENT_GROUP_NAME" == "Staging" ]
then
  sudo cp /home/www/reddimatch/config/staging/config.py /home/www/reddimatch/config.py
fi

if [ "$DEPLOYMENT_GROUP_NAME" == "Production" ]
then
  sudo cp /home/www/reddimatch/config/production/config.py /home/www/reddimatch/config.py
fi

sudo pip install virtualenv
sudo virtualenv venv
sudo chown -R ubuntu:ubuntu venv/
source venv/bin/activate
pip install -r requirements.txt

# nginx config
sudo cp config/sites-available /etc/nginx/sites-available/reddimatch
sudo ln -s /etc/nginx/sites-available/reddimatch /etc/nginx/sites-enabled/reddimatch
sudo rm /etc/nginx/sites-enabled/default

# tmp folder for logging
sudo mkdir /home/www/reddimatch/tmp
sudo chown -R ubuntu:ubuntu /home/www/reddimatch/tmp/

# set up monit
sudo cp config/monitrc /etc/monit/monitrc
sudo monit
