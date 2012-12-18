"""
Installs and configures an openstack client
"""

import logging

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-CLIENT"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack client configuration")
    paramsList = [
                  {"CMD_OPTION"      : "osclient-host",
                   "USAGE"           : "The IP address of the server on which to install the openstack client packages, an admin \"rc\" file will also be installed",
                   "PROMPT"          : "The IP address of the server on which to install the openstack client packages, an admin \"rc\" file will also be installed",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_OSCLIENT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NOVACLIENT",
                  "DESCRIPTION"           : "NOVACLIENT Config paramaters",
                  "PRE_CONDITION"         : "CONFIG_CLIENT_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CLIENT_INSTALL'] != 'y':
        return

    osclientsteps = [
             {'title': 'Creating OS Client Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Client", [], [], osclientsteps)

def createmanifest():
    manifestfile = "%s_osclient.pp"%controller.CONF['CONFIG_OSCLIENT_HOST']
    manifestdata = getManifestTemplate("openstack_client.pp")
    appendManifestFile(manifestfile, manifestdata)
