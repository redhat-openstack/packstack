# -*- coding: utf-8 -*-

"""
Installs and configures Keystone
"""

import uuid

from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


# ------------- Keystone Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Keystone"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "keystone-db-passwd",
         "USAGE": "The password to use for the Keystone to access DB",
         "PROMPT": "Enter the password for the Keystone DB access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_KEYSTONE_DB_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-region",
         "USAGE": "Region name",
         "PROMPT": "Region name",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "RegionOne",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_KEYSTONE_REGION",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-admin-token",
         "USAGE": "The token to use for the Keystone service api",
         "PROMPT": "The token to use for the Keystone service api",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex,
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_TOKEN",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-admin-passwd",
         "USAGE": "The password to use for the Keystone admin user",
         "PROMPT": "Enter the password for the Keystone admin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-demo-passwd",
         "USAGE": "The password to use for the Keystone demo user",
         "PROMPT": "Enter the password for the Keystone demo user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_KEYSTONE_DEMO_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-token-format",
         "USAGE": "Kestone token format. Use either UUID or PKI",
         "PROMPT": "Enter the Keystone token format.",
         "OPTION_LIST": ['UUID', 'PKI'],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": 'UUID',
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": 'CONFIG_KEYSTONE_TOKEN_FORMAT',
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "keystone-service-name",
         "USAGE": "Name of service to use to run keystone (keystone or httpd)",
         "PROMPT": "Enter the Keystone service name.",
         "OPTION_LIST": ['keystone', 'httpd'],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "keystone",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": 'CONFIG_KEYSTONE_SERVICE_NAME',
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "KEYSTONE",
             "DESCRIPTION": "Keystone Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    keystonesteps = [
        {'title': 'Adding Keystone manifest entries',
         'functions': [create_manifest]},
    ]
    controller.addSequence("Installing OpenStack Keystone", [], [],
                           keystonesteps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone.pp")

    fw_details = dict()
    key = "keystone"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "keystone"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['5000', '35357']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_KEYSTONE_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_KEYSTONE_RULES')
    appendManifestFile(manifestfile, manifestdata)
