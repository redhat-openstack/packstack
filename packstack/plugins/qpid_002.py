"""
Installs and configures qpid
"""

import logging

from packstack.installer import validators
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-QPID"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack QPID configuration")
    paramsList = [
                  {"CMD_OPTION"      : "qpid-host",
                   "USAGE"           : "The IP address of the server on which to install the QPID service",
                   "PROMPT"          : "Enter the IP address of the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "QPIDLANCE",
                  "DESCRIPTION"           : "QPID Config parameters",
                  "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    # If we don't want Nova we don't need qpid
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return
    qpidsteps = [
             {'title': 'Adding QPID manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing QPID", [], [], qpidsteps)

def createmanifest():
    manifestfile = "%s_qpid.pp"%controller.CONF['CONFIG_QPID_HOST']
    manifestdata = getManifestTemplate("qpid.pp")
    appendManifestFile(manifestfile, manifestdata, 'pre')
