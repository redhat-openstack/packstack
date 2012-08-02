"""
Installs and configures nova api
"""

import logging
import os
import uuid


import engine_validators as validate
import basedefs
import common_utils as utils

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-NOVAAPI"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = 'puppet/manifests'
PUPPET_MANIFEST_TEMPLATE = 'puppet/templates/nova_api.pp'

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Nova API configuration")
    paramsList = [
                  {"CMD_OPTION"      : "novaapi-host",
                   "USAGE"           : "Hostname of the Nova API server",
                   "PROMPT"          : "Hostname of the Nova API server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVAAPI_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NOVAAPI",
                  "DESCRIPTION"           : "NOVAAPI Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    novaapisteps = [
             {'title': 'Creating Nova API Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Nova API", [], [], novaapisteps)

def createmanifest():
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, "%s_api_nova.pp"%controller.CONF['CONFIG_NOVAAPI_HOST'])
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)

    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(manifestdata)

