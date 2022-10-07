import ipaddress
import sys

import click
import validators
from click import Context
from pynetbox.core.api import Api


@click.group()
def ip():
    pass


def validate_ipv4(ctx, param, value):
    try:
        return ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError as e:
        raise click.BadParameter(str(e))


@ip.command(help='Create or update IP Address records with the given reverse DNS. The subnet mask is automatically '
                 'set to the same as the parent prefix.')
@click.option('--start', '-s', 'start_ip', help='Start IP', required=True, callback=validate_ipv4)
@click.option('--end', '-e', 'end_ip', help='End IP', required=True, callback=validate_ipv4)
@click.option('--format', '-f', 'dns_format', help='Reverse DNS format. Use {1} for octet 1, {2} for octet 2 etc',
              required=True)
@click.option('--dry-run', '-n', is_flag=True, help='Dry run, don\'t actually set DNS')
@click.option('--allow-all', '-a', is_flag=True,
              help='Also allow setting what would be the subnet\'s network and broadcast addresses')
@click.pass_context
def set_reverse(ctx: Context, start_ip: ipaddress.IPv4Address, end_ip: ipaddress.IPv4Address, dns_format: str,
                dry_run: bool = False, allow_all: bool = False):
    netbox: Api = ctx.obj['netbox']

    if start_ip > end_ip:
        print('End address must be equal to or higher than the start address.', file=sys.stderr)
        sys.exit(1)

    # Find a prefix that covers start_ip:

    prefix = find_longest_prefix_containing_ip(netbox, start_ip)

    if not prefix:
        print('No Netbox prefix found that covers %s' % str(start_ip), file=sys.stderr)
        sys.exit(1)

    prefix_net = ipaddress.IPv4Network(prefix.prefix)
    prefix_len = prefix_net.prefixlen

    # Check that end_ip is in the same prefix

    if end_ip not in prefix_net:
        print(
            'The end address %s is not in the same prefix %s as the start address %s.' % (str(end_ip), str(prefix_net),
                                                                                          str(start_ip)),
            file=sys.stderr)
        sys.exit(1)

    # Check that we're not accidentally setting the network or broadcast addresses

    if not allow_all and (start_ip == prefix_net.network_address or start_ip == prefix_net.broadcast_address or
                          end_ip == prefix_net.network_address or end_ip == prefix_net.broadcast_address):
        print('You have requested to include the network/broadcast address and not specified --allow-all.',
              file=sys.stderr)
        sys.exit(1)

    # Loop the addresses and create or update their IP Address records:

    created = updated = unchanged = 0
    ip = start_ip
    while ip <= end_ip:
        ip_int: ipaddress.IPv4Interface = ipaddress.IPv4Interface('%s/%d' % (str(ip), prefix_len))

        # get the current record if it exists
        nb_ip = netbox.ipam.ip_addresses.get(address=str(ip_int))

        dns_name = dns_format.format(str(ip_int.ip),
                                     ip_int.ip.packed[0],
                                     ip_int.ip.packed[1],
                                     ip_int.ip.packed[2],
                                     ip_int.ip.packed[3])

        if not validators.domain(dns_name):
            print('Given format string would produce illegal reverse DNS "%s" for %s.' % (dns_name, str(ip_int)),
                  file=sys.stderr)
            sys.exit(1)

        if nb_ip:
            if nb_ip.dns_name == dns_name:
                print('UNCHANGED: %s -> %s' % (str(ip_int), dns_name))
                unchanged += 1
            else:
                print('UPDATE: %s -> %s (was %s)' % (str(ip_int), dns_name, nb_ip.dns_name))
                updated += 1
                if not dry_run:
                    nb_ip.dns_name = dns_name
                    nb_ip.save()
        else:
            print('CREATE: %s -> %s' % (str(ip_int), dns_name))
            created += 1
            if not dry_run:
                netbox.ipam.ip_addresses.create(address=str(ip_int),
                                                dns_name=dns_name)

        ip += 1

    print('%d created, %d updated, %d unchanged.' % (created, updated, unchanged))
    if dry_run:
        print('Dry run, nothing was changed.')


def find_longest_prefix_containing_ip(netbox, ip):
    prefixes = netbox.ipam.prefixes.filter(contains=str(ip))
    found_prefix = None
    found_prefix_length = None
    for prefix in prefixes:
        subnet = ipaddress.IPv4Network(prefix.prefix)
        if found_prefix is None or subnet.prefixlen > found_prefix_length:
            found_prefix = prefix
            found_prefix_length = subnet.prefixlen
    return found_prefix


COMMANDS = [ip]
