"""
Installs and configures qpid
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
PLUGIN_NAME = "OS-QPID"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/manifests')
PUPPET_MANIFEST_TEMPLATE = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/templates/qpid.pp')

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack QPID configuration")
    paramsList = [
                  {"CMD_OPTION"      : "qpid-host",
                   "USAGE"           : "Hostname of the QPID server",
                   "PROMPT"          : "Hostname of the QPID server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "QPIDLANCE",
                  "DESCRIPTION"           : "QPID Config paramaters",
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
             {'title': 'Creating QPID Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing QPID", [], [], qpidsteps)

def createmanifest():
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, "%s_qpid.pp"%controller.CONF['CONFIG_QPID_HOST'])
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)

    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(manifestdata)

