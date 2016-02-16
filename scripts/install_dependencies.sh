#!/bin/bash
export AWS_DEFAULT_REGION=us-west-2

get_ami_tags () {
    instance_id=$(curl --silent http://169.254.169.254/latest/meta-data/instance-id)
    echo $(aws ec2 describe-tags --filters "Name=resource-id,Values=$instance_id")
}

tags_to_env () {
    tags=$1

    for key in $(echo $tags | jq -r ".[][].Key"); do
        value=$(echo $tags | jq -r ".[][] | select(.Key==\"$key\") | .Value")
        key=$(echo $key | tr '-' '_' | tr '[:lower:]' '[:upper:]')
        export $key="$value"
    done
}

instance_tags=$(get_instance_tags)

tags_to_env "$instance_tags"

sudo apt-get -y update
sudo apt-get -y install build-essential libssl-dev libffi-dev python-dev git libmysqlclient-dev monit python-pip nginx jq
