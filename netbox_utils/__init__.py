import os
import sys
from configparser import ConfigParser

import click
import pynetbox
from click import Context
from pynetbox.core.api import Api

from netbox_utils import secrets, nbdns


def load_config(config_file) -> ConfigParser:
    if config_file:
        config = ConfigParser()
        if config.read(config_file):
            return config
        else:
            print('Config file %s could not be loaded' % config_file, file=sys.stderr)
            sys.exit(1)

    files = [
        os.path.join(os.path.expanduser('~'), '.config', 'netbox-utils', 'netbox-utils.conf'),
        'netbox-utils.conf'
    ]

    for file in files:
        if os.path.exists(file):
            config = ConfigParser()
            if config.read(file):
                return config
            # else:
            #     _LOGGER.warning("%s found but could not be loaded", file)

    # TODO validate all required keys are present
    return ConfigParser()


def get_api(config, verbose=False) -> Api:
    nb = pynetbox.api(config['api'], config['token'],
                      private_key=config['private_key'] if 'private_key' in config else None,
                      private_key_file=config['private_key_file'] if 'private_key_file' in config else None
                      )

    # Call the status method to test the connection
    nb_status = nb.status()
    if verbose:
        print("Connected to Netbox version %s at %s" % (nb_status['netbox-version'], config['api']))

    return nb


@click.group()
@click.pass_context
@click.option('--config', '-c', 'config_file',
              help='Alternate netbox-utils.conf file (defaults to ~/.config/netbox-utils/netbox-utils.conf)')
@click.option('--section', '-s', 'config_section', default='DEFAULT',
              help='Alternate config section to use (defaults to DEFAULT)')
@click.option('--verbose', '-v', 'verbose', is_flag=True,
              help='Verbose connection')
def cli(ctx: Context, config_file: str, config_section: str, verbose: bool):
    ctx.ensure_object(dict)

    root_config = load_config(config_file)

    if config_section not in root_config:
        print('No config section %s found in config' % config_section, file=sys.stderr)
        sys.exit(1)

    ctx.obj['config'] = root_config[config_section]

    ctx.obj['verbose'] = verbose
    ctx.obj['netbox'] = get_api(ctx.obj['config'], verbose)


@cli.command()
@click.pass_context
def shell(ctx: Context):
    import code
    code.interact(local={'nb': ctx.obj['netbox']}, banner="Netbox API is in 'nb' object", exitmsg='')  # local=locals())

for command in secrets.COMMANDS + nbdns.COMMANDS:
    cli.add_command(command)
