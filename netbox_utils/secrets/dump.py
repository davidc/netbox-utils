from operator import attrgetter

import click
from click import Context


@click.command()
@click.pass_context
def dump(ctx: Context):
    nb = ctx.obj['netbox']
    devices = list(nb.dcim.devices.all())

    devices.sort(key=attrgetter('site.name', 'device_role.name', 'name'))

    secrets = list(nb.secrets.secrets.all())
    secrets.sort(key=attrgetter('role.name', 'name'))

    cursite = None
    curdevice = None

    for device in devices:
        if device.site.name != cursite:
            print('Site: %s' % (device.site.name))
            cursite = device.site.name
        if device.name != curdevice:
            print(' Device: %s' % (device.name), end='')
            if device.primary_ip4:
                print(' (%s)' % device.primary_ip4.address.split('/')[0], end='')
            if device.primary_ip6:
                print(' (%s)' % device.primary_ip6.address.split('/')[0], end='')
            print()
            curdevice = device.name

        mysecrets = (x for x in secrets if
                     x.assigned_object_type == 'dcim.device' and x.assigned_object_id == device.id)
        for secret in mysecrets:
            print('  (%s) %s = %s' % (secret.role.name, secret.name, secret.plaintext))


COMMANDS = [dump]
