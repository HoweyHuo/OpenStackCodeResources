import os
import sys
import time
import json
from pprint import pprint
import CloudStack
import hcnotify
import uuid

from fabric.api import *
from fabric.contrib.files import exists, append, contains, sed, comment

def config_env(ip, key_path):
	env.user = 'ubuntu'
	env.hosts=ip
	env.key_filename = key_path
	env.disable_known_hosts = True

def remove_cloud_init():
	sudo('apt-get purge -y cloud-init')

def update_fstab_mount_vdb():
	#TODO: Here we probably need a detect function to make sure the vdb are there and are correct in size
	# format /dev/vdb: mkfs.ext4 /dev/vdb
	sudo('mkfs.ext4 /dev/vdb')
	# make dir /data to mount drive
	sudo('mkdir /data')
	# add to fstab: /dev/vdb /data ext4 rw 0 0
	append('/etc/fstab', '/dev/vdb /data ext4 rw 0 0', use_sudo=True)
	# run mount -av to mount the drive
	sudo('mount -av')
	# display mount result
	sudo('lsblk')

ntpUsPool = """
server 0.us.pool.ntp.org iburst
server 1.us.pool.ntp.org iburst
server 2.us.pool.ntp.org iburst
server 3.us.pool.ntp.org iburst
"""
def config_ntp_chrony_sync():
	sudo('apt-get -y install chrony')
	comment('/etc/chrony/chrony.conf','server ..debian.pool.ntp.org', use_sudo=True, char='#', backup='.bak')
	append('/etc/chrony/chrony.conf',ntpUsPool,True)
	sudo('service chrony restart')

def openstack_packages_deploy():
	sudo('apt-get install -y software-properties-common')
	sudo('add-apt-repository -y cloud-archive:liberty')
	sudo('apt-get update')
	sudo('apt-get -y dist-upgrade')
	sudo('apt-get install -y python-openstackclient')

def mariadb_server_deploy():
	sudo('apt-get install -y mariadb-server python-pymysql')
	#TODO: add configuration change according to http://docs.openstack.org/liberty/install-guide-ubuntu/environment-sql-database.html
	#TODO: use tool "expect" to run mysql_secure_installation script

def mongodb_deploy():
	sudo('apt-get install -y mongodb-server mongodb-clients python-pymongo')
	#TODO: add script to change bind_ip = 127.0.0.1 into bind_ip = 192.168.122.250
	#TODO: add script to add line smallfiles = true

def rabbitmq_server_deploy():
	sudo('apt-get install -y rabbitmq-server')
	sudo('rabbitmqctl add_user openstack RABBIT_PASS')
	sudo('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')