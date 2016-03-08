from fabric.api import *
from fabric.contrib.files import exists, append, contains, sed, comment

def config_env(ip, key_path):
	env.user = 'ubuntu'
	env.hosts=ip
	env.key_filename = key_path
	env.disable_known_hosts = True

def test_logger():
	run('logger "Howey Says Test"')
