"""
Installs and configures nova common
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
PLUGIN_NAME = "OS-NOVACOMMON"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = 'puppet/manifests'
PUPPET_MANIFEST_TEMPLATE = 'puppet/templates/nova_common.pp'

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Nova Common configuration")
    paramsList = [
                 ]

    groupDict = { "GROUP_NAME"            : "NOVACOMMON",
                  "DESCRIPTION"           : "NOVACOMMON Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    novacommonsteps = [
             {'title': 'Creating Nova Common Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Nova Common", [], [], novacommonsteps)

def createmanifest():
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)

    for manifestfile in controller.CONF['CONFIG_MANIFESTFILES']:
        if manifestfile.endswith("_nova.pp"):
            with open(manifestfile, 'a') as fp:
                fp.write("\n")
                fp.write(manifestdata)


