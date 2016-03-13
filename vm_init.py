#! /usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################################################################################
#
# Python Script to create VM with KVM hypervisor
#
################################################################################################################################################

import common_library as commonlib
import json
import os
from optparse import OptionParser
import sys
import time


def main():
    params = parse_params()
    vm_config = validate_config(params["vm_config"])
    vm_ip = create_vm(vm_config)


def validate_config(config_filename):
    print("Try to use vm_config file: %s" % config_filename)
    if not os.path.isfile(config_filename):
        print("vm_config file %s does not exists!" % config_filename)
        sys.exit(-2)
    config_data = open(config_filename)
    vm_config = json.load(config_data)
    if not vm_config.has_key("name"):
        print("VM configuration file invalid, Missing [Name ]")
        sys.exit(-3)
    if os.path.exists(vm_config["name"]):
        print("VM folder %s already exists. Exit!" % vm_config["name"])
        sys.exit(-3)
    return vm_config


def create_vm(vm_config):
    result = commonlib.ShellOut("uvt-kvm list | grep %s" % vm_config["name"])
    if vm_config["name"] in result["output"]:
        print("VM %s already exists, Exit!" % vm_config["name"])
        sys.exit(0)

    print("Create VM folder " + vm_config["name"])
    os.system("mkdir " + vm_config["name"])

    print("Copy over fabric provisioning script")
    os.system("cp fabfile.py ./%s/" % vm_config["name"])

    print("Copy over bootstrap script")
    os.system("cp vm_bootstrap.sh ./%s/" % vm_config["name"])

    print("Copy Public and Private key pair over for ubuntu user access")
    os.system("cp " + vm_config["key_name"] + "* ./" + vm_config["name"] + "/")

    print("use uvt-kvm to create VM according to vm_config")
    vm_create_cmd = "uvt-kvm create " + \
                        vm_config["cpu"] + " " + \
                        vm_config["root_disk_gb"] + " " +\
                        vm_config["memory_mb"] + " " +\
                        "--run-script-once ./" + vm_config["name"] + "/vm_bootstrap.sh " + \
                        "--ssh-public-key-file ./" + vm_config["name"] + "/" + vm_config["key_name"] + ".pub " + \
                        vm_config["name"] + " release=trusty"
    print("Command line: " + vm_create_cmd)
    os.system(vm_create_cmd)

    result = commonlib.ShellOut("uvt-kvm list | grep %s" % vm_config["name"])
    if vm_config["name"] in result["output"]:
        print("VM %s created" % vm_config["name"])
    else:
        print("Failed to create VM " + vm_config["name"])
        sys.exit(-5)

    vm_wait_cmd = "uvt-kvm wait --ssh-private-key-file ./" + vm_config["name"] + "/" + vm_config["key_name"] + " --insecure " + \
                  vm_config["name"]
    print("Wait for VM provisioning finish with uvt-kvm wait command: " + vm_wait_cmd)
    os.system(vm_wait_cmd)
    print("VM " + vm_wait_cmd + " provision completed, try to get IP address and run fabric on it")

    result = commonlib.ShellOut("uvt-kvm ip " + vm_config["name"])
    if result["status"] == 0:
        vm_ip = result["output"]
        print("VM IP Address: " + vm_ip)
    else:
        print("Failed to get ip for VM " + vm_config["name"])
        sys.exit(-6)
    # At this point,the machine is ready to stand by its own. so we are going to remove its cloudinit disk
    # First download all information into XML to read
    dumpXmlcmd = "virsh dumpxml " + vm_config["name"]
    print("run Virsh Command to dump XML out of KVM")
    result = commonlib.ShellOut(dumpXmlcmd)
    # print(result)
    # TODO: We need to collect the Cloud_init data drive image information and remove it accordingly.
    # TODO: For now we will just use hard coded path for this. /var/lib/uvtool/libvirt/images/{vm_name}-ds.qcow

    fab_cmd = "fab config_env:" + vm_ip + ",./" + vm_config["name"] + "/" + vm_config["key_name"] + " remove_cloud_init"
    print("run fabric task to remove cloud_init: " + fab_cmd)

    while True:
        result = commonlib.ShellOut(fab_cmd)
        print(result["output"])
        if result["status"] == 0:
            print("Completed")
            break
        else:
            print("Failed to remove Cloud_init from guest system,sleep 10 seconds and try again")
            time.sleep(10)


    detachVDBcmd = "virsh detach-disk " + vm_config["name"] + " vdb --persistent"
    print("remove vdb from vm, using virsh command: " + detachVDBcmd)
    os.system(detachVDBcmd)

    print("Sleep for 5 seconds, wait for disk really detached")
    # TODO: Here we need to add real check function to check disk really detached
    time.sleep(5)

    shutdownVMcmd = "virsh shutdown " + vm_config["name"]
    print("Shutdown VM " + vm_config["name"] + "with Virsh Command:" + shutdownVMcmd)
    os.system(shutdownVMcmd)

    print("Sleep for 5 seconds, wait for machine shutdown")
    # TODO: Here we need to add real check function to check machine really down before do anything else
    time.sleep(5)

    volDeletecmd = "virsh vol-delete " + vm_config["name"] + "-ds.qcow --pool uvtool"
    print("remove vdb from vm, using virsh command: " + volDeletecmd)
    os.system(volDeletecmd)

    print("Sleep for 5 seconds, wait for volume really deleted")
    # TODO: Here we need to add real check function to check volume is really deleted
    time.sleep(5)

    startVMcmd = "virsh start " + vm_config["name"]
    print("Start VM " + vm_config["name"] + "with Virsh Command:" + startVMcmd)
    os.system(startVMcmd)

    print("Sleep for 5 seconds, wait for machine startup")
    # TODO: Here we need to add real check function to check machine really up before do anything else
    time.sleep(5)

    
    current_dir = os.getcwd()
    create_img_cmd = "qemu-img create -f qcow2 -o preallocation=metadata ./" + vm_config["name"] + "/" + vm_config["name"] + "-disk2.qcow2 " + vm_config["second_disk_gb"] + "G"
    print("Create " + vm_config["second_disk_gb"] + "GB drive as second hard drive: " + create_img_cmd)
    os.system(create_img_cmd)
    time.sleep(10)

    attach_disk_cmd = "virsh attach-disk " + vm_config["name"] + " --source " + current_dir + "/" +  vm_config["name"] + "/" + vm_config["name"] + "-disk2.qcow2 --target vdb --persistent"
    #TODO: here we might need to have script to determine the available device. for now, just Hard Code it
    print("attach dirve image to VM: " + attach_disk_cmd)
    os.system(attach_disk_cmd)
    time.sleep(5)

    fab_cmd = "fab config_env:" + vm_ip + ",./" + vm_config["name"] + "/" + vm_config["key_name"] + " update_fstab_mount_vdb"
    print("run fabric tasks to mount new disk to /data: " + fab_cmd)
    result = commonlib.ShellOut(fab_cmd)
    print(result["output"])
    return vm_ip


def parse_params():
    usage_str = """use vm_init to create VM.
in order to create VM please provide configuration file for vm in JSON format
USUAGE:
	vm_init.py {config_file_name.json}
"""
    params = {}
    parser = OptionParser(usage=usage_str)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("please provide configuration file for the VM")
        sys.exit(-1)
    params["vm_config"] = args[0]
    return params


if __name__ == "__main__":
    main()
