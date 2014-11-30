# -*- coding: utf-8 -*-

"""
Installs and configures Glance
"""

from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)

# ------------- Glance Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Glance"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "glance-db-passwd",
         "USAGE": "The password to use for the Glance to access DB",
         "PROMPT": "Enter the password for the Glance DB access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_GLANCE_DB_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "glance-ks-passwd",
         "USAGE": ("The password to use for the Glance to authenticate "
                   "with Keystone"),
         "PROMPT": "Enter the password for the Glance Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_GLANCE_KS_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "glance-backend",
         "USAGE": ("Glance storage backend controls how Glance stores disk "
                   "images. Supported values: file, swift. Note that Swift "
                   "installation have to be enabled to have swift backend "
                   "working. Otherwise Packstack will fallback to 'file'."),
         "PROMPT": "Glance storage backend",
         "OPTION_LIST": ["file", "swift"],
         "VALIDATORS": [validators.validate_options],
         "PROCESSORS": [process_backend],
         "DEFAULT_VALUE": "file",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_GLANCE_BACKEND",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "GLANCE",
             "DESCRIPTION": "Glance Config parameters",
             "PRE_CONDITION": "CONFIG_GLANCE_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    conf = controller.CONF
    if conf['CONFIG_GLANCE_INSTALL'] != 'y':
        if conf['CONFIG_NOVA_INSTALL'] == 'y':
            raise RuntimeError('Glance is required to install Nova properly. '
                               'Please set CONFIG_GLANCE_INSTALL=y')
        return

    glancesteps = [
        {'title': 'Adding Glance Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Glance manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Glance", [], [], glancesteps)


# ------------------------- helper functions -------------------------

def process_backend(value, param_name, config):
    if value == 'swift' and config['CONFIG_SWIFT_INSTALL'] != 'y':
        return 'file'
    return value


# -------------------------- step functions --------------------------

def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_glance.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_glance.pp" % config['CONFIG_STORAGE_HOST']
    manifestdata = getManifestTemplate("glance.pp")
    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        mq_template = get_mq(config, "glance_ceilometer")
        manifestdata += getManifestTemplate(mq_template)

    fw_details = dict()
    key = "glance_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "glance"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['9292']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_GLANCE_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_GLANCE_RULES')
    appendManifestFile(manifestfile, manifestdata)
