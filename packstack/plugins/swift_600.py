"""
Installs and configures an openstack swift
"""

import logging
import os

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile, manifestfiles

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SWIFT"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack swift configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-swift-proxy",
                   "USAGE"           : "The IP address on which to install the Swift proxy service",
                   "PROMPT"          : "Enter the IP address of the Swift proxy service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_PROXY_HOSTS", # TO-DO: Create processor for CSV
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage",
                   "USAGE"           : "A comma seperated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device, if /dev is ommited packstack will create a loopback device for a test setup",
                   "PROMPT"          : "Enter the Swift Storage servers e.g. host/dev,host/dev",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_HOSTS", # TO-DO: Create processor for CSV
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-zones",
                   "USAGE"           : "Number of swift storage zones, this number MUST be no bigger then number of storage devices configured",
                   "PROMPT"          : "Enter the number of swift storage zones, MUST be no bigger then number of storage devices configured",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateInteger,
                   "DEFAULT_VALUE"   : "1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_ZONES",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-replicas",
                   "USAGE"           : "Number of swift storage replicas, this number MUST be no bigger then number of storage zones configured",
                   "PROMPT"          : "Enter the number of swift storage replicas, MUST be no bigger then number of storage zones configured",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateInteger,
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
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "ext4",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE_FSTYPE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSSWIFT",
                  "DESCRIPTION"           : "OpenStack Swift Config paramaters",
                  "PRE_CONDITION"         : "CONFIG_SWIFT_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_SWIFT_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Swift Keystone Manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Creating OS Swift builder Manifests', 'functions':[createbuildermanifest]},
             {'title': 'Creating OS Swift proxy Manifests', 'functions':[createproxymanifest]},
             {'title': 'Creating OS Swift storage Manifests', 'functions':[createstoragemanifest]},
             {'title': 'Creating OS Swift Common Manifests', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing OpenStack Swift", [], [], steps)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    controller.CONF['CONFIG_SWIFT_PROXY'] = controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'].split(',')[0]
    manifestdata = getManifestTemplate("keystone_swift.pp")
    appendManifestFile(manifestfile, manifestdata)

devices = []
def parseDevices(config_swift_storage_hosts):
    device_number = 0
    for host in config_swift_storage_hosts.split(","):
        device_number += 1
        device = None
        if '/' in host:
            host, device = host.split('/')[0:2]
        zone = (device_number % int(controller.CONF["CONFIG_SWIFT_STORAGE_ZONES"]))+1
        devices.append({'host':host, 'device':device, 'device_name':'device%s'%device_number, 'zone':str(zone)})
    return devices

# The ring file should be built and distributed befor the storage services
# come up. Specifically the replicator crashes if the ring isn't present
def createbuildermanifest():
    # TODO : put this on the proxy server, will need to change this later
    controller.CONF['CONFIG_SWIFT_BUILDER_HOST'] = controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'].split(',')[0]
    manifestfile = "%s_ring_swift.pp"%controller.CONF['CONFIG_SWIFT_BUILDER_HOST']
    manifestdata = getManifestTemplate("swift_builder.pp")

    # Add each device to the ring
    devicename = 0
    for device in parseDevices(controller.CONF["CONFIG_SWIFT_STORAGE_HOSTS"]):
        host = device['host']
        devicename = device['device_name']
        zone = device['zone']

        manifestdata = manifestdata + '\n@@ring_object_device { "%s:6000/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)
        manifestdata = manifestdata + '\n@@ring_container_device { "%s:6001/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)
        manifestdata = manifestdata + '\n@@ring_account_device { "%s:6002/%s":\n zone        => %s,\n weight      => 10, }'%(host, devicename, zone)

    appendManifestFile(manifestfile, manifestdata, 'swiftbuilder')

def createproxymanifest():
    manifestfile = "%s_swift.pp"%controller.CONF['CONFIG_SWIFT_PROXY_HOSTS']
    manifestdata = getManifestTemplate("swift_proxy.pp")
    # If the proxy server is also a storage server then swift::ringsync will be included for the storage server
    if controller.CONF['CONFIG_SWIFT_PROXY_HOSTS'] not in controller.CONF["CONFIG_SWIFT_STORAGE_HOSTS"].split(","):
        manifestdata += 'swift::ringsync{["account","container","object"]:\n    ring_server => "%s"\n}'%controller.CONF['CONFIG_SWIFT_BUILDER_HOST']
    appendManifestFile(manifestfile, manifestdata)

def createstoragemanifest():

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

        server = utils.ScriptRunner(host)
        validate.r_validateDevice(server, device)
        server.execute()

        manifestfile = "%s_swift.pp"%host
        if device:
            manifestdata = "\n" + 'swift::storage::%s{"%s":\n  device => "/dev/%s",\n}'% (controller.CONF["CONFIG_SWIFT_STORAGE_FSTYPE"], devicename, device)
        else:
            controller.CONF["SWIFT_STORAGE_DEVICES"] = "'%s'"%devicename
            manifestdata = "\n" + getManifestTemplate("swift_loopback.pp")
        appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_swift.pp"):
            data = getManifestTemplate("swift_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
