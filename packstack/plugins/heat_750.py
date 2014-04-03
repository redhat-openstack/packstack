"""
Installs and configures heat
"""

import uuid
import logging
import os

from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             manifestfiles,
                                             appendManifestFile)

controller = None

# Plugin name
PLUGIN_NAME = "OS-HEAT"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Heat configuration")
    parameters = [
        {"CMD_OPTION"      : "heat-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat service'),
         "PROMPT"          : 'Enter the IP address of the Heat service',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-mysql-password",
         "USAGE"	         : 'The password used by Heat user to authenticate against MySQL',
         "PROMPT"          : "Enter the password for the Heat MySQL user",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_DB_PW",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-auth-encryption-key",
         "USAGE"           : "The encryption key to use for authentication info in database",
         "PROMPT"          : "Enter the authentication key for Heat to use for authenticate info in database",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_AUTH_ENC_KEY",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-ks-passwd",
         "USAGE"           : "The password to use for the Heat to authenticate with Keystone",
         "PROMPT"          : "Enter the password for the Heat Keystone access",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_KS_PW",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "os-heat-cloudwatch-install",
         "USAGE"           : ("Set to 'y' if you would like Packstack to "
                              "install Heat CloudWatch API"),
         "PROMPT"          : "Should Packstack install Heat CloudWatch API",
         "OPTION_LIST"     : ["y", "n"],
         "VALIDATORS"      : [validators.validate_options],
         "DEFAULT_VALUE"   : "n",
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_CLOUDWATCH_INSTALL",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "os-heat-cfn-install",
         "USAGE"           : ("Set to 'y' if you would like Packstack to "
                              "install Heat CloudFormation API"),
         "PROMPT"          : "Should Packstack install Heat CloudFormation API",
         "OPTION_LIST"     : ["y", "n"],
         "VALIDATORS"      : [validators.validate_options],
         "DEFAULT_VALUE"   : "n",
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_CFN_INSTALL",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },
        ]
    group = {"GROUP_NAME"          : "Heat",
             "DESCRIPTION"         : "Heat Config parameters",
             "PRE_CONDITION"       : "CONFIG_HEAT_INSTALL",
             "PRE_CONDITION_MATCH" : "y",
             "POST_CONDITION"      : False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, parameters)

    parameters = [
        {"CMD_OPTION"      : "heat-api-cloudwatch-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat CloudWatch API service'),
         "PROMPT"          : ('Enter the IP address of the Heat CloudWatch API '
                              'server'),
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_CLOUDWATCH_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },
    ]

    def check_cloudwatch(config):
        return config["CONFIG_HEAT_INSTALL"] == 'y' and \
            config["CONFIG_HEAT_CLOUDWATCH_INSTALL"] == 'y'

    group = {"GROUP_NAME"          : "Heat CloudWatch API",
             "DESCRIPTION"         : "Heat CloudWatch API config parameters",
             "PRE_CONDITION"       : check_cloudwatch,
             "PRE_CONDITION_MATCH" : True,
             "POST_CONDITION"      : False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, parameters)

    parameters = [
        {"CMD_OPTION"      : "heat-api-cfn-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat CloudFormation API service'),
         "PROMPT"          : ('Enter the IP address of the Heat CloudFormation '
                              'API server'),
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_CFN_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },
    ]

    def check_cloudformation(config):
        return config["CONFIG_HEAT_INSTALL"] == 'y' and \
            config["CONFIG_HEAT_CFN_INSTALL"] == 'y'

    group = {"GROUP_NAME"          : "Heat CloudFormation API",
             "DESCRIPTION"         : "Heat CloudFormation API config parameters",
             "PRE_CONDITION"       : check_cloudformation,
             "PRE_CONDITION_MATCH" : True,
             "POST_CONDITION"      : False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, parameters)


def initSequences(controller):
    if controller.CONF['CONFIG_HEAT_INSTALL'] != 'y':
        return
    steps = [{'title': 'Adding Heat manifest entries',
              'functions': [create_manifest]},
             {'title': 'Adding Heat Keystone manifest entries',
              'functions':[create_keystone_manifest]}]

    if controller.CONF.get('CONFIG_HEAT_CLOUDWATCH_INSTALL', 'n') == 'y':
        steps.append({'title': 'Adding Heat CloudWatch API manifest entries',
                      'functions': [create_cloudwatch_manifest]})
    if controller.CONF.get('CONFIG_HEAT_CFN_INSTALL', 'n') == 'y':
        steps.append({'title': 'Adding Heat CloudFormation API manifest entries',
                      'functions': [create_cfn_manifest]})
    controller.addSequence("Installing Heat", [], [], steps)


def create_manifest(config):
    if config['CONFIG_HEAT_CLOUDWATCH_INSTALL'] == 'y':
        config['CONFIG_HEAT_WATCH_HOST'] = config['CONFIG_HEAT_CLOUDWATCH_HOST']
    else:
        config['CONFIG_HEAT_WATCH_HOST'] = config['CONFIG_HEAT_HOST']
    if config['CONFIG_HEAT_CFN_INSTALL'] == 'y':
        config['CONFIG_HEAT_METADATA_HOST'] = config['CONFIG_HEAT_CFN_HOST']
    else:
        config['CONFIG_HEAT_METADATA_HOST'] = config['CONFIG_HEAT_HOST']

    manifestfile = "%s_heat.pp" % controller.CONF['CONFIG_HEAT_HOST']
    manifestdata = getManifestTemplate("heat.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_keystone_manifest(config):
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_heat.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_cloudwatch_manifest(config):
    manifestfile = "%s_heatcw.pp" % controller.CONF['CONFIG_HEAT_CLOUDWATCH_HOST']
    manifestdata = getManifestTemplate("heat_cloudwatch.pp")
    appendManifestFile(manifestfile, manifestdata, marker='heat')


def create_cfn_manifest(config):
    manifestfile = "%s_heatcnf.pp" % controller.CONF['CONFIG_HEAT_CFN_HOST']
    manifestdata = getManifestTemplate("heat_cfn.pp")
    appendManifestFile(manifestfile, manifestdata, marker='heat')
