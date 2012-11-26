"""
Installs and configures Glance
"""

import logging
import os
import uuid


import packstack.installer.engine_validators as validate
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Glance"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_TEMPLATE = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/templates/glance.pp')
PUPPET_MANIFEST_DIR      = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/manifests')

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Glance configuration")
    paramsList = [
                  {"CMD_OPTION"      : "glance-host",
                   "USAGE"           : "The IP address of the server on which to install Glance",
                   "PROMPT"          : "The IP address of the server on which to install Glance",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_GLANCE_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "GLANCE",
                  "DESCRIPTION"           : "Glance Config paramaters",
                  "PRE_CONDITION"         : "CONFIG_GLANCE_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_GLANCE_INSTALL'] != 'y':
        return

    glancesteps = [
             {'title': 'Adding Glance Keystone Manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Creating Galnce Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Glance", [], [], glancesteps)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_glance.pp")
    appendManifestFile(manifestfile, manifestdata)

def createmanifest():
    manifestfile = "%s_glance.pp"%controller.CONF['CONFIG_GLANCE_HOST']
    manifestdata = getManifestTemplate("glance.pp")
    appendManifestFile(manifestfile, manifestdata)

