import time

from fabric.api import *
from fabric.contrib.files import exists, append, contains, sed, comment

def config_env(ip, key_path):
	env.user = 'ubuntu'
	env.hosts=ip
	env.key_filename = key_path
	env.disable_known_hosts = True

def remove_cloud_init():
	sudo('apt-get purge -y cloud-init')

