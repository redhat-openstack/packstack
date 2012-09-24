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
                  {"CMD_OPTION"      : "os-dashboard-host",
                   "USAGE"           : "Hostname of the Dashoard",
                   "PROMPT"          : "Hostname of the Dashoard",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_DASHBOARD_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-dashboard-secretkey",
                   "USAGE"           : "Keystone Secret Encryption Key",
                   "PROMPT"          : "Keystone Secret Encryption Key",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : uuid.uuid4().hex,
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_DASHBOARD_SECRET_KEY",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSDASHBOARD",
                  "DESCRIPTION"           : "OpenStack Dashboard Config paramaters",
                  "PRE_CONDITION"         : "CONFIG_DASHBOARD_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_DASHBOARD_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Creating OS Dashboard Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Dashboard", [], [], steps)

def createmanifest():
    manifestfile = "%s_dashboard.pp"%controller.CONF['CONFIG_DASHBOARD_HOST']
    manifestdata = getManifestTemplate("dashboard.pp")
    appendManifestFile(manifestfile, manifestdata)
