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

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile, manifestfiles

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SWIFT"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Swift configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-swift-proxy",
                   "USAGE"           : "The IP address on which to install the Swift proxy service (currently only single proxy is supported)",
                   "PROMPT"          : "Enter the IP address of the Swift proxy service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_multi_ip, validators.validate_multi_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_PROXY_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-ks-passwd",
                   "USAGE"           : "The password to use for the Swift to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Swift Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SWIFT_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage",
                   "USAGE"           : "A comma separated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device(packstack does not create the filesystem, you must do this first), if /dev is omitted Packstack will create a loopback device for a test setup",
                   "PROMPT"          : "Enter the Swift Storage servers e.g. host/dev,host/dev",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty, validate_storage],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-zones",
                   "USAGE"           : "Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured",
                   "PROMPT"          : "Enter the number of swift storage zones, MUST be no bigger than the number of storage devices configured",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_integer],
                   "DEFAULT_VALUE"   : "1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_ZONES",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-replicas",
                   "USAGE"           : "Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured",
                   "PROMPT"          : "Enter the number of swift storage replicas, MUST be no bigger than the number of storage zones configured",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_integer],
                   "DEFAULT_VALUE"   : "1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_REPLICAS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-fstype",
                   "USAGE"           : "FileSystem type for storage nodes",
                   "PROMPT"          : "Enter FileSystem type for storage nodes",
                   "OPTION_LIST"     : ['xfs','ext4'],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "ext4",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_FSTYPE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-hash",
                   "USAGE"           : "Shared secret for Swift",
                   "PROMPT"          : "Enter hash for Swift shared secret",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SWIFT_HASH",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-size",
                   "USAGE"           : "Size of the swift loopback file storage device",
                   "PROMPT"          : "Enter the size of the storage device (eg. 2G, 2000M, 2000000K)",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate_storage_size],
                   "DEFAULT_VALUE"   : "2G",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_SIZE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                 ]

    groupDict = { "GROUP_NAME"            : "OSSWIFT",
                  "DESCRIPTION"           : "OpenStack Swift Config parameters",
                  "PRE_CONDITION"         : "CONFIG_SWIFT_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}


    controller.addGroup(groupDict, paramsList)


def validate_storage(param, options=None):
    for host in param.split(','):
        host = host.split('/', 1)[0]
        validators.validate_ip(host.strip(), options)

def validate_storage_size(param, options=None):
    match = re.match(r'\d+G|\d+M|\d+K', param, re.IGNORECASE)
    if not match:
        msg = 'Storage size not have a valid value (eg. 1G, 1000M, 1000000K)'
        raise ParamValidationError(msg)

def initSequences(controller):
    if controller.CONF['CONFIG_SWIFT_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Swift Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Swift builder manifest entries', 'functions':[createbuildermanifest]},
             {'title': 'Adding Swift proxy manifest entries', 'functions':[createproxymanifest]},
             {'title': 'Adding Swift storage manifest entries', 'functions':[createstoragemanifest]},
             {'title': 'Adding Swift common manifest entries', 'functions':[createcommonmanifest]},
    ]

    controller.addSequence("Installing OpenStack Swift", [], [], steps)


def createkeystonemanifest(config):
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    controller.CONF['CONFIG_SWIFT_PROXY'] = controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'].split(',')[0]
    manifestdata = getManifestTemplate("keystone_swift.pp")
    appendManifestFile(manifestfile, manifestdata)


devices = []
def parse_devices(config_swift_storage_hosts):
    """
    Returns dict containing information about Swift storage devices.
    """
    device_number = 0
    num_zones = int(controller.CONF["CONFIG_SWIFT_STORAGE_ZONES"])
    for host in config_swift_storage_hosts.split(","):
        host = host.strip()
        device_number += 1
        device = None
        if '/' in host:
            host, device = map(lambda x: x.strip(), host.split('/', 1))
        zone = str((device_number % num_zones) + 1)
        devices.append({'host': host, 'device': device, 'zone': zone,
                        'device_name': 'device%s' % device_number})
    return devices


# The ring file should be built and distributed befor the storage services
# come up. Specifically the replicator crashes if the ring isn't present
def createbuildermanifest(config):
    # TODO : put this on the proxy server, will need to change this later
    controller.CONF['CONFIG_SWIFT_BUILDER_HOST'] = controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'].split(',')[0]
    manifestfile = "%s_ring_swift.pp"%controller.CONF['CONFIG_SWIFT_BUILDER_HOST']
    manifestdata = getManifestTemplate("swift_builder.pp")

    # Add each device to the ring
    devicename = 0
    for device in parse_devices(controller.CONF["CONFIG_SWIFT_STORAGE_HOSTS"]):
        host = device['host']
        devicename = device['device_name']
        zone = device['zone']

        manifestdata = manifestdata + '\n@@ring_object_device { "%s:6000/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)
        manifestdata = manifestdata + '\n@@ring_container_device { "%s:6001/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)
        manifestdata = manifestdata + '\n@@ring_account_device { "%s:6002/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)

    appendManifestFile(manifestfile, manifestdata, 'swiftbuilder')


def createproxymanifest(config):
    manifestfile = "%s_swift.pp"%controller.CONF['CONFIG_SWIFT_PROXY_HOSTS']
    manifestdata = getManifestTemplate("swift_proxy.pp")
    # If the proxy server is also a storage server then swift::ringsync will be included for the storage server
    if controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'] not in [h['host'] for h in devices]:
        manifestdata += 'swift::ringsync{["account","container","object"]:\n    ring_server => "%s"\n}'%controller.CONF['CONFIG_SWIFT_BUILDER_HOST']
    appendManifestFile(manifestfile, manifestdata)


def check_device(host, device):
    """
    Raises ScriptRuntimeError if given device is not mounted on given
    host.
    """
    server = utils.ScriptRunner(host)

    # the device MUST exist
    cmd = 'ls -l /dev/%s'
    server.append(cmd % device)

    # if it is not mounted then we can use it
    cmd = 'grep "/dev/%s " /proc/self/mounts || exit 0'
    server.append(cmd % device)

    # if it is mounted then the mount point has to be in /srv/node
    cmd = 'grep "/dev/%s /srv/node" /proc/self/mounts && exit 0'
    server.append(cmd % device)

    # if we got here without exiting then we can't use this device
    server.append('exit 1')
    server.execute()
    return False

def get_storage_size(size):
    ranges = {'G': 1048576, 'M': 1024, 'K': 1}
    size.strip()
    for measure in ['G', 'M', 'K']:
        if re.match('\d+' + measure, size, re.IGNORECASE):
            intsize = int(size.rstrip(measure)) * ranges[measure]
            return intsize

def createstoragemanifest(config):

    # this need to happen once per storage host
    for host in set([device['host'] for device in devices]):
        controller.CONF["CONFIG_SWIFT_STORAGE_CURRENT"] = host
        manifestfile = "%s_swift.pp"%host
        manifestdata = getManifestTemplate("swift_storage.pp")
        appendManifestFile(manifestfile, manifestdata)

    # this need to happen once per storage device
    for device in devices:
        host = device['host']
        devicename = device['device_name']
        device = device['device']
        if device:
            check_device(host, device)

        manifestfile = "%s_swift.pp"%host
        if device:
            manifestdata = "\n" + 'swift::storage::%s{"%s":\n  device => "/dev/%s",\n}'% (controller.CONF["CONFIG_SWIFT_STORAGE_FSTYPE"], devicename, device)
        else:
            config['SWIFT_STORAGE_SEEK'] = get_storage_size(config['CONFIG_SWIFT_STORAGE_SIZE'])
            controller.CONF["SWIFT_STORAGE_DEVICES"] = "'%s'"%devicename
            manifestdata = "\n" + getManifestTemplate("swift_loopback.pp")
        appendManifestFile(manifestfile, manifestdata)

    # set allowed hosts for firewall
    swift_hosts = get_swift_hosts(config)
    hosts = swift_hosts.copy()
    manifestdata = ""
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        hosts |= split_hosts(config['CONFIG_NOVA_COMPUTE_HOSTS'])

    config['FIREWALL_SERVICE_NAME'] = "swift storage and rsync"
    config['FIREWALL_PORTS'] = "['6000', '6001', '6002', '873']"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    for host in hosts:
        config['FIREWALL_ALLOWED'] = "'%s'" % host
        config['FIREWALL_SERVICE_ID'] = "swift_storage_and_rsync_%s" % host
        manifestdata += getManifestTemplate("firewall.pp")

    for host in swift_hosts:
        manifestfile = "%s_swift.pp" % host
        appendManifestFile(manifestfile, manifestdata)


def createcommonmanifest(config):
    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_swift.pp"):
            data = getManifestTemplate("swift_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)


def get_swift_hosts(config):
    """Get a set of all the Swift hosts"""
    hosts = split_hosts(config['CONFIG_SWIFT_STORAGE_HOSTS'])
    # remove "/device" from the storage host names
    hosts = set(host.split('/', 1)[0] for host in hosts)
    hosts |= split_hosts(config['CONFIG_SWIFT_PROXY_HOSTS'])
    return hosts
