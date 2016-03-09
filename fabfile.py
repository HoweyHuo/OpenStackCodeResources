import time

from fabric.api import *
from fabric.contrib.files import exists, append, contains, sed, comment

def config_env(ip, key_path):
	env.user = 'ubuntu'
	env.hosts=ip
	env.key_filename = key_path
	env.disable_known_hosts = True

def remove_cloud_init():
	while True:
		res = sudo('apt-get purge -y cloud-init')
		print("get result from sudo apt-get purge:" + res)
		if "out: E: Could not get lock /var/lib/dpkg/lock - open" in res:
			print("Failed to get dpkg lock, wait 10 seconds and try again")
			time.sleep(10)
		else:
			break;

