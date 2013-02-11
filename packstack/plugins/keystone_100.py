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
    logging.debug("Adding OpenStack Keystone configuration")
    paramsList = [
                  {"CMD_OPTION"      : "keystone-host",
                   "USAGE"           : "The IP address of the server on which to install Keystone",
                   "PROMPT"          : "Enter the IP address of the Keystone server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "keystone-db-passwd",
                   "USAGE"           : "The password to use for the Keystone to access DB",
                   "PROMPT"          : "Enter the password for the Keystone DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "keystone-admin-token",
                   "USAGE"           : "The token to use for the Keystone service api",
                   "PROMPT"          : "The token to use for the Keystone service api",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex,
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_ADMINTOKEN",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "keystone-admin-passwd",
                   "USAGE"           : "The password to use for the Keystone admin user",
                   "PROMPT"          : "Enter the password for the Keystone admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_KEYSTONE_ADMINPASSWD",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "KEYSTONE",
                  "DESCRIPTION"           : "Keystone Config parameters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    keystonesteps = [
             {'title': 'Adding Keystone manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Keystone", [], [], keystonesteps)

def createmanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone.pp")
    appendManifestFile(manifestfile, manifestdata)
