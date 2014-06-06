# -*- coding: utf-8 -*-

"""
Installs and configures heat
"""

import uuid
import logging
import os

from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             manifestfiles,
                                             appendManifestFile)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Heat"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    parameters = [
        {"CMD_OPTION": "os-heat-mysql-password",
         "USAGE": ('The password used by Heat user to authenticate against '
                   'MySQL'),
         "PROMPT": "Enter the password for the Heat MySQL user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_DB_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "heat-auth-encryption-key",
         "USAGE": ("The encryption key to use for authentication info "
                   "in database"),
         "PROMPT": ("Enter the authentication key for Heat to use for "
                    "authenticate info in database"),
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_AUTH_ENC_KEY",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-ks-passwd",
         "USAGE": ("The password to use for the Heat to authenticate "
                   "with Keystone"),
         "PROMPT": "Enter the password for the Heat Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_KS_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-cloudwatch-install",
         "USAGE": ("Set to 'y' if you would like Packstack to install Heat "
                   "CloudWatch API"),
         "PROMPT": "Should Packstack install Heat CloudWatch API",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_CLOUDWATCH_INSTALL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-cfn-install",
         "USAGE": ("Set to 'y' if you would like Packstack to install Heat "
                   "CloudFormation API"),
         "PROMPT": "Should Packstack install Heat CloudFormation API",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_CFN_INSTALL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "Heat",
             "DESCRIPTION": "Heat Config parameters",
             "PRE_CONDITION": "CONFIG_HEAT_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, parameters)


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_HEAT_INSTALL'] != 'y':
        return
    steps = [
        {'title': 'Adding Heat manifest entries',
         'functions': [create_manifest]},
        {'title': 'Adding Heat Keystone manifest entries',
         'functions': [create_keystone_manifest]}
    ]

    if config.get('CONFIG_HEAT_CLOUDWATCH_INSTALL', 'n') == 'y':
        steps.append(
            {'title': 'Adding Heat CloudWatch API manifest entries',
             'functions': [create_cloudwatch_manifest]})
    if config.get('CONFIG_HEAT_CFN_INSTALL', 'n') == 'y':
        steps.append(
            {'title': 'Adding Heat CloudFormation API manifest entries',
             'functions': [create_cfn_manifest]})
    controller.addSequence("Installing Heat", [], [], steps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    manifestfile = "%s_heat.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "heat"))
    manifestdata += getManifestTemplate("heat.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_heat.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_cloudwatch_manifest(config, messages):
    manifestfile = "%s_heatcw.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "heat"))
    manifestdata += getManifestTemplate("heat_cloudwatch.pp")
    appendManifestFile(manifestfile, manifestdata, marker='heat')


def create_cfn_manifest(config, messages):
    manifestfile = "%s_heatcnf.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "heat"))
    manifestdata += getManifestTemplate("heat_cfn.pp")
    appendManifestFile(manifestfile, manifestdata, marker='heat')
