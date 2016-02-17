#!/bin/bash
# start nginx
sudo service nginx start

# run app
sudo nginx -s reload

# db migration
cd /home/www/reddimatch
source venv/bin/activate
python db_upgrade.py

get_ami_tags () {
    instance_id=$(curl --silent http://169.254.169.254/latest/meta-data/instance-id)
    echo $(aws ec2 describe-tags --filters "Name=resource-id,Values=$instance_id")
}

get_instance_tags () {
    ami_id=$(curl --silent http://169.254.169.254/latest/meta-data/ami-id)
    echo $(aws ec2 describe-tags --filters "Name=resource-id,Values=$ami_id")
}

tags_to_env () {
    tags=$1

    for key in $(echo $tags | jq -r ".[][].Key"); do
        value=$(echo $tags | jq -r ".[][] | select(.Key==\"$key\") | .Value")
        key=$(echo $key | tr '-' '_' | /usr/bin/tr '[:lower:]' '[:upper:]')
        export $key="$value"
    done
}

ami_tags=$(get_ami_tags)
instance_tags=$(get_instance_tags)

tags_to_env "$ami_tags"
tags_to_env "$instance_tags"

gunicorn --worker-class eventlet wsgi -b 0.0.0.0:8000 -D -p /home/www/reddimatch/tmp/gunicorn.pid
