#!/usr/bin/env python3

import argparse
import netboxutil
from pprint import pprint

parser = argparse.ArgumentParser(description='Connect to Netbox API for interactive use.')
netboxutil.add_default_args(parser)

args = parser.parse_args()
config = netboxutil.handle_args(args)

nb = netboxutil.get_api(config, verbose=True)

import code
code.interact(local={'nb': nb}, banner="Netbox API is in 'nb' object", exitmsg='') # local=locals())

