# -*- coding: utf-8 -*-

"""
Installs and configures Ceilometer
"""

import logging
import os
import uuid

from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Ceilometer"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    ceilometer_params = {
        "CEILOMETER": [
            {"CONF_NAME": "CONFIG_CEILOMETER_SECRET",
             "CMD_OPTION": "ceilometer-secret",
             "USAGE": "Secret key for signing metering messages",
             "PROMPT": "Enter the Ceilometer secret key",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": uuid.uuid4().hex[:16],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": True,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_CEILOMETER_KS_PW",
             "CMD_OPTION": "ceilometer-ks-passwd",
             "USAGE": ("The password to use for Ceilometer to authenticate "
                       "with Keystone"),
             "PROMPT": "Enter the password for the Ceilometer Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
        ],

        "MONGODB": [
            {"CMD_OPTION": "mongodb-host",
             "USAGE": ("The IP address of the server on which to install "
                       "MongoDB"),
             "PROMPT": "Enter the IP address of the MongoDB server",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_MONGODB_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
    }

    ceilometer_groups = [
        {"GROUP_NAME": "CEILOMETER",
         "DESCRIPTION": "Ceilometer Config parameters",
         "PRE_CONDITION": "CONFIG_CEILOMETER_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "MONGODB",
         "DESCRIPTION": "MONGODB Config parameters",
         "PRE_CONDITION": "CONFIG_CEILOMETER_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in ceilometer_groups:
        paramList = ceilometer_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def initSequences(controller):
    if controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y':
        return

    steps = [{'title': 'Adding MongoDB manifest entries',
              'functions': [create_mongodb_manifest]},
             {'title': 'Adding Ceilometer manifest entries',
              'functions': [create_manifest]},
             {'title': 'Adding Ceilometer Keystone manifest entries',
              'functions': [create_keystone_manifest]}]
    controller.addSequence("Installing OpenStack Ceilometer", [], [],
                           steps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    manifestfile = "%s_ceilometer.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "ceilometer"))
    manifestdata += getManifestTemplate("ceilometer.pp")

    fw_details = dict()
    key = "ceilometer_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "ceilometer-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8777']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_CEILOMETER_RULES'] = fw_details
    manifestdata += createFirewallResources('FIREWALL_CEILOMETER_RULES')

    # Add a template that creates a group for nova because the ceilometer
    # class needs it
    if config['CONFIG_NOVA_INSTALL'] == 'n':
        manifestdata += getManifestTemplate("ceilometer_nova_disabled.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_mongodb_manifest(config, messages):
    manifestfile = "%s_mongodb.pp" % config['CONFIG_MONGODB_HOST']
    manifestdata = getManifestTemplate("mongodb.pp")

    fw_details = dict()
    key = "mongodb_server"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "%s" % config['CONFIG_CONTROLLER_HOST']
    fw_details[key]['service_name'] = "mongodb-server"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['27017']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MONGODB_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_MONGODB_RULES')
    appendManifestFile(manifestfile, manifestdata, 'pre')


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_ceilometer.pp")
    appendManifestFile(manifestfile, manifestdata)
