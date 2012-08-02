"""
Installs and configures nova sched
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
PLUGIN_NAME = "OS-NOVASCHED"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = 'puppet/manifests'
PUPPET_MANIFEST_TEMPLATE = 'puppet/templates/nova_sched.pp'

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Nova Sched configuration")
    paramsList = [
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "Hostname of the Nova Sched server",
                   "PROMPT"          : "Hostname of the Nova Sched server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVASCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NOVASCHED",
                  "DESCRIPTION"           : "NOVASCHED Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    novaschedsteps = [
             {'title': 'Creating Nova Sched Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Nova Sched", [], [], novaschedsteps)

def createmanifest():
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, "%s_nova.pp"%controller.CONF['CONFIG_NOVASCHED_HOST'])
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)

    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(manifestdata)

