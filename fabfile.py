import time
import fabric

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
