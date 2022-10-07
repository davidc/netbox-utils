Utilities for getting data into and out of Netbox

### Reverse DNS generation

Use `netbox-utils ip set-reverse` to automatically create or update IP address records with reverse DNS according to a
format string. Use {1} to {4} to access the octets of the address in the format string.

```shell
netbox-utils -s mycompany ip set-reverse -s 10.218.22.197 -e 10.218.22.222 -f "camera-{1}-{2}-{3}-{4}.surveillance.mycompany.com"
```
