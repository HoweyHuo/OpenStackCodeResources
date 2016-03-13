#! /usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################################################################################
#
# Python Script to destroy VM with KVM hypervisor
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
    
    if not destroy_vm_uvt(params["vm_name"]) and not destroy_vm_virsh(params["vm_name"]):
        print ("Failed to remove VM " + params["vm_name"])
        sys.exit(-2)

    rm_cmd = "rm -rf " + params["vm_name"]
    os.system(rm_cmd)

        
def destroy_vm_uvt(vm_name):
    destroy_cmd = "uvt-kvm destroy " + vm_name
    res = os.system(destroy_cmd)
    if res == 0:
        print("VM " +  vm_name + " Destroyed. now remove custom VM control folder")
        os.system(rm_cmd)
        print("Folder " + vm_name + " removed!")
        return True
    else:
        print("Failed to destroy VM " + vm_name + " with uvt-kvm")
        return False

def destroy_vm_virsh(vm_name):
    destroy_cmd = "virsh undefine " + vm_name
    res = os.system(destroy_cmd)
    if res != 0:
        return False
    poolrefresh_cmd = "virsh pool-refresh uvtool"
    res = os.system(poolrefresh_cmd)
    if res != 0:
        return False

    voldelete_cmd = "virsh vol-delete " + vm_name + ".qcow --pool uvtool"
    res = os.system(voldelete_cmd)
    if res != 0:
        return False     
    return True

def parse_params():
    usage_str = """use vm_destroy to destroy VM.
in order to destroy VM please provide vm_name
USUAGE:
	vm_destroy.py {vm_name}
"""
    params = {}
    parser = OptionParser(usage=usage_str)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("please provide VM Name")
        sys.exit(-1)
    params["vm_name"] = args[0]
    return params

if __name__ == "__main__":
    main()
