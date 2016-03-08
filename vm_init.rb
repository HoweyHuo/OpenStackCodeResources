#!/usr/bin/env ruby

################################################################################################################################################
#
# Ruby Script to create VM with KVM hypervisor
#
################################################################################################################################################

require 'json'
require_relative('common_library')

def usuage
	@usuage=<<-EOS
use vm_init to create VM.
in order to create VM please provide configuration file for vm in JSON format
USUAGE:
	vm_init.rb vm_config={config_file_name.json}
EOS
	puts @usuage
end

$params = set_params
# Need to provide JSON formated VM configuration file before creating it
if $params["vm_config"]==nil
	usuage
	raise "Argument Exception: Please provide VM configuration JSON file"
end
# make sure the provided VM configuration file path is correct
if !File.exist?($params["vm_config"])
	usuage
	raise "Argument Exception: VM Configuration file #{ $params["vm_config"] } does not exists"
end

@vm_config_file = File.read($params["vm_config"])
@vm_config = JSON.parse(@vm_config_file)

if @vm_config["name"] == nil
	raise "VM configuration file invalid, Missing [Name ]"
end
if Dir.exists?(@vm_config["name"] )
	puts "VM folder #{ @vm_config["name"]  } already exists. Exit!"
	exit(0)
end

@result = ShellOut("uvt-kvm list | grep #{ @vm_config["name"]  }")
if @result["output"].include?(@vm_config["name"])
	puts "VM #{ @vm_config["name"] } already exists. Exit!"
	exit(0)
end

puts "Create VM folder #{ @vm_config["name"] }"
`mkdir #{ @vm_config["name"] }`

puts "Copy over fabric provisioning script"
`cp fabfile.py ./#{ @vm_config["name"] }/`

puts "Copy over bootstrap script"
`cp vm_bootstrap.sh ./#{ @vm_config["name"] }/`

puts "Copy Public and Private key pair over for ubuntu user access"
`cp ubuntu_ssh_key.pem* ./#{ @vm_config["name"] }/`

puts "use uvt-kvm to create VM according to vm_config: #{ $params["vm_config"] }"
@vm_create_cmd = "uvt-kvm create #{ @vm_config["cpu"] } #{ @vm_config["root_disk_gb"] } --run-script-once ./#{ @vm_config["name"] }/vm_bootstrap.sh --ssh-public-key-file ./#{ @vm_config["name"] }/ubuntu_ssh_key.pem.pub #{ @vm_config["name"] } release=wily"
puts "Command line: #{ @vm_create_cmd }"
`#{ @vm_create_cmd }`
@result = ShellOut("uvt-kvm list | grep #{ @vm_config["name"]  }")
if @result["output"].include?(@vm_config["name"])
	puts "VM #{ @vm_config["name"]  } created"
else
	raise "Failed to create VM #{ @vm_config["name"]  }"
end

@vm_wait_cmd = "uvt-kvm wait --ssh-private-key-file ./#{ @vm_config["name"] }/ubuntu_ssh_key.pem --insecure #{ @vm_config["name"] }"
puts "Wait for VM provisioning finish with uvt-kvm wait command: #{ @vm_wait_cmd }"
@result =  ShellOut(@vm_wait_cmd)

puts "VM #{ @vm_wait_cmd } provision completed, try to get IP address and run fabric on it"

@result = ShellOut("uvt-kvm ip #{ @vm_config["name"]  }")
if @result["success"]
	@vm_ip = @result["output"]
	puts "VM IP Address: #{ @vm_ip }"
else
	raise "Failed to get ip for VM #{ @vm_config["name"]  }"
end

@fab_cmd = "fab config_env:#{ @vm_ip },./#{ @vm_config["name"] }//ubuntu_ssh_key.pem test_logger"
puts "run fabric tasks to config environment accordingly: #{ @fab_cmd }"
@result = ShellOut(@fab_cmd)
if @result["success"]
	puts "Completed"
else
	puts "Failed"
end
puts @result["output"]

