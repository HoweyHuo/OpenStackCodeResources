#! /bin/bash

# update apt-get repository
apt-get update
# remove cloud init from this machine. so we can also remove the attached disk
sudo apt-get purge -y cloud-init