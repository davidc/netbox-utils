from setuptools import setup, find_packages

setup(
    name='netbox-utils',
    version='0.0.1',
    url='https://github.com/davidc/netbox-utils',
    license='TBD',
    author='david',
    author_email='David Croft',
    description='Netbox importers/exporters',
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        'click',
        'pynetbox',
        'napalm',
        'prompt_toolkit',
    ],
    entry_points={
        'console_scripts': [
            'netbox-utils = netbox_utils:cli',
        ],
    },

)
