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
    destroy_cmd = "uvt-kvm destroy " + params["vm_name"]
    res = os.system(destroy_cmd)
    if res == 0:
        rm_cmd = "rm -rf " + params["vm_name"]
        os.system(rm_cmd)
    else:
        print("Failed to destroy VM " + params["vm_name"] + ".")
        print("Please delete manually")
        sys.exit(-1)

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
