#!/usr/bin/env python3

import argparse
import netboxutil
import os
import ipaddress
import socket

parser = argparse.ArgumentParser(description='Import interfaces.')
netboxutil.add_default_args(parser)

args = parser.parse_args()
config = netboxutil.handle_args(args)

nb = netboxutil.get_api(config, verbose=True)



histfile = os.path.join(os.path.expanduser('~'), '.config', 'netbox-util', 'import_interfaces.history')
        

from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

def error(msg):
    print_formatted_text(FormattedText([('red', msg)]))

def warning(msg):
    print_formatted_text(FormattedText([('goldenrod', msg)]))
    
def info(msg):
    print_formatted_text(FormattedText([('khaki', msg)]))
    

prompt_session = PromptSession(history=FileHistory(histfile))


# Get all the VMs for the autocompletion
vm_names = [ vm.name for vm in nb.virtualization.virtual_machines.all() ]
vm_completer = WordCompleter(vm_names, match_middle=True)



def loop_vm():
    try:
        while True:

            print()

            prompt_session.completer = vm_completer
            vm_name = prompt_session.prompt([('teal italic', 'VM?'), ('', ' ')])
            prompt_session.completer = None

            if vm_name == '':
                continue
    
            try:
                vm = nb.virtualization.virtual_machines.get(name=vm_name)
            except ValueError as e:
                print(e)
                continue

            if vm is None:
                error('No VM found with this name.')
                continue
    
            loop_interface(vm)


    except KeyboardInterrupt:
        return

            
def loop_interface(vm):
    
    try:
        while True:

            print()

            existing_interfaces = [x for x in nb.virtualization.interfaces.filter(virtual_machine_id=vm.id)]

            existing_interface_names = [ x.name for x in existing_interfaces ]
            existing_interface_completer = WordCompleter(existing_interface_names, match_middle=True)

            
            if len(existing_interfaces) > 0:
                #            print(len(existing_interfaces))
                info('Existing interfaces: ' + ' '.join(existing_interface_names))
                default_interface = existing_interface_names[0] if len(existing_interfaces) == 1 else ''
            else:
                info('No existing interfaces')
                default_interface = ''

            prompt_session.completer = existing_interface_completer
            interface_name = prompt_session.prompt('%s → Interface? ' % (vm.name), default=default_interface)
            prompt_session.completer = None
            
            if interface_name == '':
                return

            interface_id = None
            for existing_interface in existing_interfaces:
                if existing_interface.name == interface_name:
                    interface_id = existing_interface.id
                    break

            if interface_id is None:
                warning('Interface %s doesn\'t exist, will be created' % (interface_name))
                
                interface_id = create_interface(vm, interface_name)

                if interface_id is None:
                    return # user cancelled interface creation

            loop_ip(vm, interface_id, interface_name)

    except KeyboardInterrupt:
        return


def create_interface(vm, interface_name):
    ip_text = prompt_session.prompt('%s → %s → VLAN? ' % (vm.name, interface_name))
    

def loop_ip(vm, interface_id, interface_name):

    try:
        while True:
            print()

            ip_text = prompt_session.prompt('%s → %s → IP address? ' % (vm.name, interface_name))

            if ip_text == '':
                return
            
            try:
                ip_address = ipaddress.ip_address(ip_text)
            except ValueError as e:
                print(e)
                continue

            # TODO check it doesn't exist (on this or any other)
            # TODO check prefix it's in exists
        
            try:
                default_dns_name = socket.gethostbyaddr(str(ip_address))[0]
            except socket.herror as e:
                warning('%s has no existing DNS entry' % (ip_address))
                default_dns_name = ''
                #        print(default_dns_name)
    
            print()
            dns_name = prompt_session.prompt('%s → %s → %s → DNS name? ' % (vm.name, interface_name, str(ip_address)), default=default_dns_name)

            if dns_name == '':
                return

    except KeyboardInterrupt:
        return


    
try:
    loop_vm()
except (KeyboardInterrupt, EOFError):
    pass # fall through to exit

