"""
Installs and configures an openstack horizon
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
PLUGIN_NAME = "OS-HORIZON"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack horizon configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-horizon-host",
                   "USAGE"           : "The IP address of the server on which to install Horizon",
                   "PROMPT"          : "The IP address of the server on which to install Horizon",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_HORIZON_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-horizon-secretkey",
                   "USAGE"           : "Keystone Secret Encryption Key",
                   "PROMPT"          : "Keystone Secret Encryption Key",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : uuid.uuid4().hex,
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_HORIZON_SECRET_KEY",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSHORIZON",
                  "DESCRIPTION"           : "OpenStack Horizon Config paramaters",
                  "PRE_CONDITION"         : "CONFIG_HORIZON_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_HORIZON_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Creating OS Horizon Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)

def createmanifest():
    manifestfile = "%s_horizon.pp"%controller.CONF['CONFIG_HORIZON_HOST']
    manifestdata = getManifestTemplate("horizon.pp")
    appendManifestFile(manifestfile, manifestdata)
