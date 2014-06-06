# -*- coding: utf-8 -*-

"""
Installs and configures an OpenStack Swift
"""

import os
import re
import uuid
import logging

from packstack.installer import validators
from packstack.installer.exceptions import ParamValidationError
from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer.utils import split_hosts

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile, manifestfiles)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Swift"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "os-swift-ks-passwd",
         "USAGE": ("The password to use for the Swift to authenticate "
                   "with Keystone"),
         "PROMPT": "Enter the password for the Swift Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_SWIFT_KS_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-storages",
         "USAGE": ("A comma separated list of devices which to use as Swift "
                   "Storage device. Each entry should take the format "
                   "/path/to/dev, for example /dev/vdb will install /dev/vdb "
                   "as Swift storage device (packstack does not create "
                   "the filesystem, you must do this first). If value is "
                   "omitted Packstack will create a loopback device for test "
                   "setup"),
         "PROMPT": "Enter the Swift Storage devices e.g. /path/to/dev",
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": '',
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGES",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_SWIFT_STORAGE_HOSTS']},

        {"CMD_OPTION": "os-swift-storage-zones",
         "USAGE": ("Number of swift storage zones, this number MUST be "
                   "no bigger than the number of storage devices configured"),
         "PROMPT": ("Enter the number of swift storage zones, MUST be no "
                    "bigger than the number of storage devices configured"),
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_integer],
         "DEFAULT_VALUE": "1",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGE_ZONES",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-storage-replicas",
         "USAGE": ("Number of swift storage replicas, this number MUST be "
                   "no bigger than the number of storage zones configured"),
         "PROMPT": ("Enter the number of swift storage replicas, MUST be no "
                    "bigger than the number of storage zones configured"),
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_integer],
         "DEFAULT_VALUE": "1",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGE_REPLICAS",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-storage-fstype",
         "USAGE": "FileSystem type for storage nodes",
         "PROMPT": "Enter FileSystem type for storage nodes",
         "OPTION_LIST": ['xfs', 'ext4'],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "ext4",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGE_FSTYPE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-hash",
         "USAGE": "Shared secret for Swift",
         "PROMPT": "Enter hash for Swift shared secret",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_SWIFT_HASH",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-storage-size",
         "USAGE": "Size of the swift loopback file storage device",
         "PROMPT": ("Enter the size of the storage device (eg. 2G, 2000M, "
                    "2000000K)"),
         "OPTION_LIST": [],
         "VALIDATORS": [validate_storage_size],
         "DEFAULT_VALUE": "2G",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGE_SIZE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "OSSWIFT",
             "DESCRIPTION": "OpenStack Swift Config parameters",
             "PRE_CONDITION": "CONFIG_SWIFT_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_SWIFT_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Adding Swift Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Swift builder manifest entries',
         'functions': [create_builder_manifest]},
        {'title': 'Adding Swift proxy manifest entries',
         'functions': [create_proxy_manifest]},
        {'title': 'Adding Swift storage manifest entries',
         'functions': [create_storage_manifest]},
        {'title': 'Adding Swift common manifest entries',
         'functions': [create_common_manifest]},
    ]
    controller.addSequence("Installing OpenStack Swift", [], [], steps)


#------------------------- helper functions -------------------------

def validate_storage_size(param, options=None):
    match = re.match(r'\d+G|\d+M|\d+K', param, re.IGNORECASE)
    if not match:
        msg = 'Storage size not have a valid value (eg. 1G, 1000M, 1000000K)'
        raise ParamValidationError(msg)


def parse_devices(config):
    """
    Returns dict containing information about Swift storage devices.
    """
    devices = []
    device_number = 0
    num_zones = int(config["CONFIG_SWIFT_STORAGE_ZONES"])
    for device in config["CONFIG_SWIFT_STORAGES"].split(","):
        device = device.strip()
        if not device:
            continue
        device_number += 1
        zone = str((device_number % num_zones) + 1)
        devices.append({'device': device, 'zone': zone,
                        'device_name': 'device%s' % device_number})
    if not devices:
        devices.append({'device': None, 'zone': 1,
                        'device_name': 'swiftloopback'})
    return devices


def check_device(host, device):
    """
    Raises ScriptRuntimeError if given device is not mounted on given
    host.
    """
    server = utils.ScriptRunner(host)

    # the device MUST exist
    cmd = 'ls -l %s'
    server.append(cmd % device)

    # if it is not mounted then we can use it
    cmd = 'grep "%s " /proc/self/mounts || exit 0'
    server.append(cmd % device)

    # if it is mounted then the mount point has to be in /srv/node
    cmd = 'grep "%s /srv/node" /proc/self/mounts && exit 0'
    server.append(cmd % device)

    # if we got here without exiting then we can't use this device
    server.append('exit 1')
    server.execute()


def get_storage_size(config):
    ranges = {'G': 1048576, 'M': 1024, 'K': 1}
    size = config['CONFIG_SWIFT_STORAGE_SIZE'].strip()
    for measure in ['G', 'M', 'K']:
        if re.match('\d+' + measure, size, re.IGNORECASE):
            intsize = int(size.rstrip(measure)) * ranges[measure]
            return intsize


#-------------------------- step functions --------------------------

def create_keystone_manifest(config, messages):
    # parse devices in first step
    global devices
    devices = parse_devices(config)
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_swift.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_builder_manifest(config, messages):
    global devices
    # The ring file should be built and distributed before the storage services
    # come up. Specifically the replicator crashes if the ring isn't present

    def device_def(dev_type, host, dev_port, devicename, zone):
        fmt = ('\n@@%s { "%s:%s/%s":\n'
               '  zone   => %s,\n'
               '  weight => 10, }\n')
        return fmt % (dev_type, host, dev_port, devicename, zone)

    manifestfile = "%s_ring_swift.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("swift_builder.pp")

    # Add each device to the ring
    devicename = 0
    for device in devices:
        host = config['CONFIG_CONTROLLER_HOST']
        devicename = device['device_name']
        zone = device['zone']
        for dev_type, dev_port in [('ring_object_device', 6000),
                                   ('ring_container_device', 6001),
                                   ('ring_account_device', 6002)]:
            manifestdata += device_def(dev_type, host, dev_port, devicename,
                                       zone)
    appendManifestFile(manifestfile, manifestdata, 'swiftbuilder')


def create_proxy_manifest(config, messages):
    manifestfile = "%s_swift.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("swift_proxy.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_storage_manifest(config, messages):
    global devices

    manifestfile = "%s_swift.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("swift_storage.pp")

    # this need to happen once per storage device
    for device in devices:
        host = config['CONFIG_CONTROLLER_HOST']
        devicename = device['device_name']
        device = device['device']
        fstype = config["CONFIG_SWIFT_STORAGE_FSTYPE"]
        if device:
            check_device(host, device)
            manifestdata += ('\nswift::storage::%s { "%s":\n'
                             '  device => "%s",\n}\n'
                             % (fstype, devicename, device))
        else:
            # create loopback device if none was specified
            config['CONFIG_SWIFT_STORAGE_SEEK'] = get_storage_size(config)
            manifestdata += "\n" + getManifestTemplate("swift_loopback.pp")

    # set allowed hosts for firewall
    hosts = set([config['CONFIG_CONTROLLER_HOST']])
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        hosts |= split_hosts(config['CONFIG_COMPUTE_HOSTS'])

    config['FIREWALL_SERVICE_NAME'] = "swift storage and rsync"
    config['FIREWALL_PORTS'] = "['6000', '6001', '6002', '873']"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    for host in hosts:
        config['FIREWALL_ALLOWED'] = "'%s'" % host
        config['FIREWALL_SERVICE_ID'] = "swift_storage_and_rsync_%s" % host
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata)


def create_common_manifest(config, messages):
    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_swift.pp"):
            data = getManifestTemplate("swift_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
