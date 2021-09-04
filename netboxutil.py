#!/usr/bin/env python3

import pynetbox
#from pprint import pprint
import os
import configparser
#import ipaddress
import sys
#import jinja2

def add_default_args(parser):

    parser.add_argument('-c', '--conf', nargs=1,
                        help='A file containing the connection configuration.')
    
#    parser.add_argument('-u', '--url', nargs=1,
#                        help='The URL of the Netbox API.')


def handle_args(args):
    if args.conf:
        if not os.path.isfile(args.conf[0]):
            print("Specified configuration file %s is not a file." % args.conf[0], file=sys.stderr)
            sys.exit(1)
        conffile = args.conf[0]
    else:
        conffile = os.path.join(os.path.expanduser('~'), '.config', 'netbox-util', 'netbox.cfg')

    config = configparser.ConfigParser()
    config.read(conffile)

    # if section specified, use it, else use DEFAULT
    # for now, use DEFAULT

    return config['DEFAULT']


def get_api(config, verbose=False):
    nb = pynetbox.api(config['api'], config['token'],
                      private_key=config['private_key'] if 'private_key' in config else None,
                      private_key_file=config['private_key_file'] if 'private_key_file' in config else None
    )

    # Call the status method to test the connection
    nb_status = nb.status()
    if verbose:
        print("Connected to Netbox version %s at %s" % (nb_status['netbox-version'], config['api']))
    
    return nb
