# -*- coding: utf-8 -*-

"""
Installs and configures Ceilometer
"""

import logging
import os
import uuid

from packstack.installer import utils
from packstack.installer import validators
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Ceilometer"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Ceilometer configuration")
    paramsList = [
        {"CMD_OPTION"      : "ceilometer-host",
         "USAGE"           : ("The IP address of the server on which "
                              "to install Ceilometer"),
         "PROMPT"          : ("Enter the IP address of the Ceilometer "
                              "server"),
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_CEILOMETER_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False},

        {"CMD_OPTION"      : "ceilometer-secret",
         "USAGE"           : "Secret key for signing metering messages.",
         "PROMPT"          : "Enter the Ceilometer secret key",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_CEILOMETER_SECRET",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False},

        {"CMD_OPTION"      : "ceilometer-ks-passwd",
         "USAGE"           : "The password to use for Ceilometer to authenticate with Keystone",
         "PROMPT"          : "Enter the password for the Ceilometer Keystone access",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_CEILOMETER_KS_PW",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False},
    ]

    groupDict = {"GROUP_NAME"          : "CEILOMETER",
                 "DESCRIPTION"         : "Ceilometer Config parameters",
                 "PRE_CONDITION"       : "CONFIG_CEILOMETER_INSTALL",
                 "PRE_CONDITION_MATCH" : "y",
                 "POST_CONDITION"      : False,
                 "POST_CONDITION_MATCH": True}
    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y':
        return

    steps = [{'title': 'Adding Ceilometer manifest entries',
              'functions': [create_manifest]},
             {'title': 'Adding Ceilometer Keystone manifest entries',
              'functions': [create_keystone_manifest]}]
    controller.addSequence("Installing OpenStack Ceilometer",[], [],
                           steps)


def create_manifest(config):
    manifestfile = "%s_ceilometer.pp" % config['CONFIG_CEILOMETER_HOST']
    manifestdata = getManifestTemplate("ceilometer.pp")
    config['FIREWALL_ALLOWED'] = "'ALL'"
    config['FIREWALL_SERVICE_NAME'] = 'ceilometer-api'
    config['FIREWALL_SERVICE_ID'] = 'ceilometer_api'
    config['FIREWALL_PORTS'] = "'8777'"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    manifestdata += getManifestTemplate("firewall.pp")
    # Add a template that creates a group for nova because the ceilometer
    # class needs it
    if config['CONFIG_NOVA_INSTALL'] == 'n':
        manifestdata += getManifestTemplate("ceilometer_nova_disabled.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_keystone_manifest(config):
    manifestfile = "%s_keystone.pp" % config['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_ceilometer.pp")
    appendManifestFile(manifestfile, manifestdata)
