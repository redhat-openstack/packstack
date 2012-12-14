"""
Plugin responsible for setting Openstack global options
"""

import logging

import packstack.installer.engine_validators as validate
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import gethostlist, PackStackException, getIP

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-GLOBAL"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "os-glance-install",
                   "USAGE"           : "Selects if packstack does or does not install Glance",
                   "PROMPT"          : "Selects if packstack does or does not install Glance",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-cinder-install",
                   "USAGE"           : "Selects if packstack does or does not install Cinder",
                   "PROMPT"          : "Selects if packstack does or does not install Cinder",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-nova-install",
                   "USAGE"           : "Selects if packstack does or does not install Nova",
                   "PROMPT"          : "Selects if packstack does or does not install Nova",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-horizon-install",
                   "USAGE"           : "Selects if packstack does or does not install Horizon",
                   "PROMPT"          : "Selects if packstack does or does not install Horizon",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_HORIZON_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-install",
                   "USAGE"           : "Selects if packstack does or does not install swift",
                   "PROMPT"          : "Selects if packstack does or does not install swift",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SWIFT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-client-install",
                   "USAGE"           : "Selects if packstack does or does not install the openstack client packages, a admin \"rc\" file will also be installed",
                   "PROMPT"          : "Selects if packstack does or does not install the openstack client packages, a admin \"rc\" file will also be installed",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CLIENT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "GLOBAL",
                  "DESCRIPTION"           : "Global Options",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    preparesteps = [
             {'title': 'Sanitizing config variable', 'functions':[sanitize]}
    ]
    controller.addSequence("Global", [], [], preparesteps)

# If either of localhost or 127.0.0.1 are anywhere in the list of hosts
# then this MUST be an all in one and all hosts MUST be loopback addresses
def dontMixloopback():
    hosts =  gethostlist(controller.CONF)

    loopback = [h for h in hosts if h in ['127.0.0.1','localhost']]
    if loopback:
        if len(loopback) != len(hosts):
            msg = "You must use 127.0.0.1 or localhost for All in One installs Only"
            print msg
            raise PackStackException(msg)

# Parts of the puppet modules MUST have IP addresses, we translate them here
# availableto templates so they are 
def translateIPs():
    hosts = []
    for key,value in controller.CONF.items():
        if key.endswith("_HOST"):
            host = value.split('/')[0] # some host have devices in the name eg 1.1.1.1/vdb
            controller.CONF[key.replace('_HOST','_IP')] = value.replace(host, getIP(host))
                
        if key.endswith("_HOSTS"):
            ips = []
            for host_dev in value.split(","):
                host_dev = host_dev.strip()
                host = host_dev.split('/')[0]
                ips.append(host_dev.replace(host, getIP(host)))
            controller.CONF[key.replace('_HOSTS','_IPS')] = ','.join(ips)

def sanitize():
    dontMixloopback()
    translateIPs()
