# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Installs and configures Swift
"""

import netaddr
import re
import uuid

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer.exceptions import ParamValidationError
from packstack.installer import utils
from packstack.installer.utils import split_hosts

from packstack.modules.documentation import update_params_usage

# ------------- Swift Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Swift"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "os-swift-ks-passwd",
         "PROMPT": "Enter the password for the Swift Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_SWIFT_KS_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-swift-storages",
         "PROMPT": "Enter the Swift Storage devices e.g. /path/to/dev",
         "OPTION_LIST": [],
         "VALIDATORS": [validate_storage],
         "DEFAULT_VALUE": '',
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SWIFT_STORAGES",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_SWIFT_STORAGE_HOSTS']},

        {"CMD_OPTION": "os-swift-storage-zones",
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
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
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
        {'title': 'Preparing Swift builder entries',
         'functions': [create_builder_manifest]},
        {'title': 'Preparing Swift proxy entries',
         'functions': [create_proxy_manifest]},
        {'title': 'Preparing Swift storage entries',
         'functions': [create_storage_manifest]},
    ]
    controller.addSequence("Installing OpenStack Swift", [], [], steps)


# ------------------------- helper functions -------------------------

def validate_storage(param, options=None):
    if not param:
        return
    if not param.startswith('/'):
        raise ParamValidationError(
            'Storage value has to be in format "/path/to/device".'
        )


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
        # we have to get rid of host part in case deprecated parameter
        # CONFIG_SWIFT_STORAGE_HOSTS has been used
        if ':' in device:
            device = device.split(':')[1]
        # device should be empty string in case only IP address has been used
        try:
            netaddr.IPAddress(device)
        except Exception:
            device = device.strip()
        else:
            device = ''

        if not device:
            continue
        device_number += 1
        zone = str((device_number % num_zones) + 1)
        devices.append({'device': device, 'zone': zone,
                        'device_name': 'device%s' % device_number})
    if not devices:
        devices.append({'device': None, 'zone': 1,
                        'device_name': 'swiftloopback'})
        config['CONFIG_SWIFT_LOOPBACK'] = 'y'
    else:
        config['CONFIG_SWIFT_LOOPBACK'] = 'n'
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
        if re.match(r'\d+' + measure, size, re.IGNORECASE):
            intsize = int(size.rstrip(measure)) * ranges[measure]
            return intsize


# -------------------------- step functions --------------------------


def create_builder_manifest(config, messages):
    global devices
    devices = parse_devices(config)
    # The ring file should be built and distributed before the storage services
    # come up. Specifically the replicator crashes if the ring isn't present

    def device_def(dev_type, host, dev_port, devicename, zone):
        # device host has to be IP address
        host = utils.force_ip(host)
        fmt = ('\n@@%s { "%s:%s/%s":\n'
               '  zone   => %s,\n'
               '  weight => 10, }\n')
        return fmt % (dev_type, host, dev_port, devicename, zone)

    # Add each device to the ring
    devicename = 0
    for configkey, dev_type, dev_port in (
        [('SWIFT_RING_OBJECT_DEVICES', 'ring_object_device', 6000),
         ('SWIFT_RING_CONTAINER_DEVICES', 'ring_container_device', 6001),
         ('SWIFT_RING_ACCOUNT_DEVICES', 'ring_account_device', 6002)]):
        swift_dev_details = dict()
        host = utils.force_ip(config['CONFIG_STORAGE_HOST_URL'])
        for device in devices:
            devicename = device['device_name']
            key = "dev_%s_%s" % (host, devicename)
            swift_dev_details.setdefault(key, {})
            zone = device['zone']
            swift_dev_details[key]['name'] = "%s:%s/%s" % (host, dev_port,
                                                           devicename)
            swift_dev_details[key]['weight'] = "%s" % 10
            swift_dev_details[key]['zone'] = "%s" % zone
        config[configkey] = swift_dev_details


def create_proxy_manifest(config, messages):
    fw_details = dict()
    key = "swift_proxy"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "swift proxy"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8080']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_SWIFT_PROXY_RULES'] = fw_details


def create_storage_manifest(config, messages):
    global devices

    devicename = 0
    swift_dev_details = dict()
    host = utils.force_ip(config['CONFIG_STORAGE_HOST_URL'])
    fstype = config["CONFIG_SWIFT_STORAGE_FSTYPE"]

    # this need to happen once per storage device
    for device in devices:
        if device['device'] is None:
            config['CONFIG_SWIFT_STORAGE_SEEK'] = get_storage_size(config)
        else:
            devicename = device['device_name']
            devicedev = device['device']
            key = "dev_%s_%s" % (host, devicename)
            swift_dev_details.setdefault(key, {})
            swift_dev_details[key]['device'] = "%s" % devicename
            swift_dev_details[key]['dev'] = "%s" % devicedev
            swift_dev_details[key]['fstype'] = "%s" % fstype
    config['CONFIG_SWIFT_STORAGE_DEVICES'] = swift_dev_details

    # set allowed hosts for firewall
    hosts = set([config['CONFIG_STORAGE_HOST']])
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        hosts |= split_hosts(config['CONFIG_COMPUTE_HOSTS'])

    fw_details = dict()
    for host in hosts:
        key = "swift_storage_and_rsync_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "swift storage and rsync"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['6000', '6001', '6002', '873']
        fw_details[key]['proto'] = "tcp"
    config['FIREWALL_SWIFT_STORAGE_RULES'] = fw_details
