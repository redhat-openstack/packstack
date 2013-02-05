"""
Installs and configures OpenStack Horizon
"""

import logging
import uuid

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
from packstack.installer import basedefs, output_messages
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
    logging.debug("Adding OpenStack Horizon configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-horizon-host",
                   "USAGE"           : "The IP address of the server on which to install Horizon",
                   "PROMPT"          : "Enter the IP address of the Horizon server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_HORIZON_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSHORIZON",
                  "DESCRIPTION"           : "OpenStack Horizon Config parameters",
                  "PRE_CONDITION"         : "CONFIG_HORIZON_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_HORIZON_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Horizon manifest entries', 'functions': [createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)

def createmanifest():
    controller.CONF["CONFIG_HORIZON_SECRET_KEY"] = uuid.uuid4().hex
    manifestfile = "%s_horizon.pp"%controller.CONF['CONFIG_HORIZON_HOST']
    manifestdata = getManifestTemplate("horizon.pp")
    appendManifestFile(manifestfile, manifestdata)
    controller.MESSAGES.append(output_messages.INFO_DASHBOARD%controller.CONF['CONFIG_HORIZON_HOST'])
