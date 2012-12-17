"""
Installs and configures Keystone
"""

import logging
import uuid


import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Keystone"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Keystone configuration")
    paramsList = [
                  {"CMD_OPTION"      : "keystone-host",
                   "USAGE"           : "The IP address of the server on which to install Keystone",
                   "PROMPT"          : "The IP address of the server on which to install Keystone",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "keystone-admin-token",
                   "USAGE"           : "The token to use for the keystone service api",
                   "PROMPT"          : "The token to use for the keystone service api",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : uuid.uuid4().hex,
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_ADMINTOKEN",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "keystone-admin-passwd",
                   "USAGE"           : "The token password to use for the keystone admin user",
                   "PROMPT"          : "The token password to use for the keystone admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:6],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_ADMINPASSWD",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "KEYSTONE",
                  "DESCRIPTION"           : "Keystone Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    keystonesteps = [
             {'title': 'Creating Keystone Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Keystone", [], [], keystonesteps)

def createmanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone.pp")
    appendManifestFile(manifestfile, manifestdata)
