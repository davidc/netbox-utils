#!/usr/bin/env python3

import argparse
import netboxutil
from pprint import pprint
from operator import attrgetter

parser = argparse.ArgumentParser(description='Output secrets from Netbox database.')
netboxutil.add_default_args(parser)

args = parser.parse_args()
config = netboxutil.handle_args(args)

nb = netboxutil.get_api(config)


devices = nb.dcim.devices.all()

devices[0].device_role.name

# Sort by device type

def sort_device(a, b):
    if a.device_role.name < b.device_role.name:
        return -1
    elif a.device_role.name > b.device_role.name:
        return +1
    if a.name < b.name:
        return -1
    elif a.name > b.name:
        return +1
    return 0


devices.sort(key=attrgetter('site.name', 'device_role.name', 'name'))

secrets = nb.secrets.secrets.all()
secrets.sort(key=attrgetter('role.name', 'name'))


cursite = None
curdevice = None

for device in devices:
    if device.site.name != cursite:
        print("Site: %s" % (device.site.name))
        cursite = device.site.name
    if device.name != curdevice:
        print(" Device: %s" % (device.name))
        curdevice = device.name
    mysecrets = (x for x in secrets if x.device.id == device.id)
    for secret in mysecrets:
        print("  (%s) %s = %s" % (secret.role.name, secret.name, secret.plaintext))
    





#for secret in secrets:
#    pprint(secret.plaintext)

