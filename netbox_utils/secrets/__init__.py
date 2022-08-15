import sys

import click
from click import Context

from netbox_utils.secrets import dump


@click.group()
@click.pass_context
def secrets(ctx: Context):
    if ctx.obj['netbox'].private_key is None:
        print('Cannot access secrets without private_key or private_key_file set in config', file=sys.stderr)
        sys.exit(1)
    pass


for command in dump.COMMANDS:
    secrets.add_command(command)

COMMANDS = [secrets]
