"""
Plugin responsible for setting Openstack global options
"""

import logging

import packstack.installer.engine_validators as validate
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import gethostlist,\
                                            getManifestTemplate, \
                                            appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-PRESCRIPT"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "os-glance-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Glance",
                   "PROMPT"          : "Should Packstack install Glance image service",
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
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Cinder",
                   "PROMPT"          : "Should Packstack install Cinder volume service",
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
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Nova",
                   "PROMPT"          : "Should Packstack install Nova compute service",
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
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Horizon",
                   "PROMPT"          : "Should Packstack install Horizon dashboard",
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
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Swift",
                   "PROMPT"          : "Should Packstack install Swift object storage",
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
                   "USAGE"           : "Set to 'y' if you would like Packstack to install the openstack client packages. An admin \"rc\" file will also be installed",
                   "PROMPT"          : "Should Packstack install Openstack client tools",
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
    osclientsteps = [
             {'title': 'Running Pre install scripts', 'functions':[createmanifest]}
    ]
    controller.addSequence("Running Pre install scripts", [], [], osclientsteps)

def createmanifest():
    for hostname in gethostlist(controller.CONF):
        manifestfile = "%s_prescript.pp" % hostname
        manifestdata = getManifestTemplate("prescript.pp")
        appendManifestFile(manifestfile, manifestdata)