#!/bin/bash
# this shell script will exchange ssh keys with target host for target user

host=$1
user=$2

ssh-keygen -R $host
ssh-keygen -R $(dig +short $host)
ssh-keyscan -t rsa $host | tee >> $HOME/.ssh/known_hosts
ssh-keyscan $host | tee >> $HOME/.ssh/known_hosts

# ssh-copy-id -i ~/.ssh/id_rsa.pub $user@$host
ssh-copy-id -i ~/.ssh/ansible-control-host.pub $user@$host

