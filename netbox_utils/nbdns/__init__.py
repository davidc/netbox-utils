import os

import click
from click import Context

from netbox_utils.nbdns.zones_generator import ZonesGenerator


@click.group()
def dns():
    pass


@dns.command()
@click.option('--extra', '-e', 'extra_file',
              help='YAML file containing additional DNS records to add.')
@click.pass_context
def generate(ctx: Context, extra_file=None):
    if not os.path.exists('out'):
        os.mkdir('out')
    if not os.path.exists('out/zones'):
        os.mkdir('out/zones')
    if not os.path.exists('out/signed-zones'):
        os.mkdir('out/signed-zones')

    zonegen = ZonesGenerator(ctx.obj['netbox'],
                             ctx.obj['config']['soa_mname'],
                             ctx.obj['config']['soa_rname'],
                             int(ctx.obj['config']['soa_refresh']),
                             int(ctx.obj['config']['soa_retry']),
                             int(ctx.obj['config']['soa_expire']),
                             int(ctx.obj['config']['ttl']),
                             ctx.obj['config']['ns_list'].split(','),
                             )

    print("Generating zones")

    zonegen.generate_zones(ctx.obj['config']['forward_domains'].split(','))
    if extra_file:
        zonegen.add_dns_extras(extra_file)

    print("Outputting zones")

    zonegen.output_zones()

    print("Verifying zones")

    zonegen.verify_zones()


COMMANDS = [dns]
