#! /usr/bin/env python

################################################################################################################################################
#
# Common python Library file to include some common functions
# Function list
# => ShellOut
#
################################################################################################################################################


import commands
import json
import os
import sys
import urllib
import urllib2

def ShellOut(cmd, cwd=None):
	command = cmd
	if cwd is not None and os.path.exists(cwd):
		print "use " + cwd + " as current dir"
		cmd = "cd " + cwd + " && " + cmd
	return_value = {}
	print "run command" + command
	status, output = commands.getstatusoutput(command)
	return_value["output"] = output
	return_value["status"] = status
	return return_value

def http_put(put_url, data, headers):
	request = urllib2.Request(put_url, data=data, headers = headers)
	request.get_method = lambda:'PUT'
	request = urllib2.urlopen(request)
	return request.read()