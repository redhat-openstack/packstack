"""
Installs and configures an openstack dashboard
"""

import logging
import os
import uuid

import engine_validators as validate
import basedefs
import common_utils as utils
from ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-DASHBOARD"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack dashboard configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-swift-proxy",
                   "USAGE"           : "Hostname of the Swift Proxy server",
                   "PROMPT"          : "Hostname of the Swift Proxy server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_PROXY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage",
                   "USAGE"           : "Hostname of the Swift Storage servers (comma seperated)",
                   "PROMPT"          : "Hostname of the Swift Storage servers (comma seperated)",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateMultiPing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SWIFT_STORAGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-storage-fstype",
                   "USAGE"           : "FileSystem type for storage nodes",
                   "PROMPT"          : "FileSystem type for storage nodes",
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
                  "PRE_CONDITION"         : "CONFIG_OS_SWIFT_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_OS_SWIFT_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Swift Keystone Manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Creating OS Swift builder Manifests', 'functions':[createbuildermanifest]},
             {'title': 'Creating OS Swift proxy Manifests', 'functions':[createproxymanifest]},
             {'title': 'Creating OS Swift storage Manifests', 'functions':[createstoragemanifest]},
             {'title': 'Creating OS Swift Common Manifests', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing OpenStack Dashboard", [], [], steps)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_swift.pp")
    appendManifestFile(manifestfile, manifestdata)

# The ring file should be built and distributed befor the storage services 
# come up. Specifically the replicator crashes if the ring isn't present
def createbuildermanifest():
    # TODO : put this on the proxy server, will need to change this later
    manifestfile = "%s_ring_swift.pp"%controller.CONF['CONFIG_SWIFT_PROXY']
    manifestdata = getManifestTemplate("swift_builder.pp")

    # Add each device to the ring
    for host in controller.CONF["CONFIG_SWIFT_STORAGE"].split(","):
        manifestdata = manifestdata + '\n@@ring_object_device { "%s:6000/1":\n zone        => 1,\n weight      => 1, }'%host
        manifestdata = manifestdata + '\n@@ring_container_device { "%s:6001/1":\n zone        => 1,\n weight      => 1, }'%host
        manifestdata = manifestdata + '\n@@ring_account_device { "%s:6002/1":\n zone        => 1,\n weight      => 1, }'%host

    appendManifestFile(manifestfile, manifestdata)

def createproxymanifest():
    manifestfile = "%s_swift.pp"%controller.CONF['CONFIG_SWIFT_PROXY']
    manifestdata = getManifestTemplate("swift_proxy.pp")
    appendManifestFile(manifestfile, manifestdata)

def createstoragemanifest():
    for host in controller.CONF["CONFIG_SWIFT_STORAGE"].split(","):
        controller.CONF["CONFIG_SWIFT_STORAGE_CURRENT"] = host
        manifestfile = "%s_swift.pp"%host
        manifestdata = getManifestTemplate("swift_storage.pp")
        appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile in controller.CONF['CONFIG_MANIFESTFILES']:
        if manifestfile.endswith("_swift.pp"):
            data = getManifestTemplate("swift_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
