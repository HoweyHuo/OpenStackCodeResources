import os
import sys
import time
import json
from pprint import pprint
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

def add_public_interface_network(vm_name):
	second_network_attach_cmd = "virsh attach-device " + vm_config["name"] + " --file ./network_definition_template/second_network_interface.xml --persistent"
	print("run virsh command to add second network adapter:")
	print(second_network_attach_cmd)
	local(second_network_attach_cmd)
	print("setup eth1 network as public network")
	put("network_definition_template/eth1.cfg", "/etc/network/interfaces.d/eth1.cfg", True)

	print("reboot machine here")
	sudo("shutdown -r 0")
	time.sleep(10)
	run("ifconfig")






    
    
    
    