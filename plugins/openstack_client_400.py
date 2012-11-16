"""
Installs and configures an openstack client
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
PLUGIN_NAME = "OS-CLIENT"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/manifests')
PUPPET_MANIFEST_TEMPLATE = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet/templates/openstack_client.pp')


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
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, "%s_osclient.pp"%controller.CONF['CONFIG_OSCLIENT_HOST'])
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)

    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(manifestdata)

