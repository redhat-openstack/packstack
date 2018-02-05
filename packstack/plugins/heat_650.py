# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Installs and configures Heat
"""

import uuid

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Heat Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Heat"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    parameters = [
        {"CMD_OPTION": "os-heat-mysql-password",
         "PROMPT": "Enter the password for the Heat DB user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_DB_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "heat-auth-encryption-key",
         "PROMPT": ("Enter the authentication key for Heat to use for "
                    "authenticate info in database (16, 24, or 32 chars)"),
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "PROCESSORS": [processors.process_string_nofloat],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_AUTH_ENC_KEY",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-ks-passwd",
         "PROMPT": "Enter the password for the Heat Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_KS_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-cfn-install",
         "PROMPT": "Should Packstack install Heat CloudFormation API",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "y",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_CFN_INSTALL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-domain",
         "PROMPT": "Enter name of Keystone domain for Heat",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "heat",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_DOMAIN",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-domain-admin",
         "PROMPT": "Enter name of Keystone domain admin user for Heat",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "heat_admin",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_DOMAIN_ADMIN",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-heat-domain-password",
         "PROMPT": "Enter password for Keystone domain admin user for Heat",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HEAT_DOMAIN_PASSWORD",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, parameters, sectioned=False)

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
        {'title': 'Preparing Heat entries',
         'functions': [create_manifest]},
    ]

    if config.get('CONFIG_HEAT_CFN_INSTALL', 'n') == 'y':
        steps.append(
            {'title': 'Preparing Heat CloudFormation API entries',
             'functions': [create_cfn_manifest]})
    controller.addSequence("Installing Heat", [], [], steps)


# ------------------------ step functions -------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        ssl_cert_file = config['CONFIG_HEAT_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_heat.crt'
        )
        ssl_key_file = config['CONFIG_HEAT_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_heat.key'
        )
        service = 'heat'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    key = "heat"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "heat"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8004']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_HEAT_RULES'] = fw_details


def create_cfn_manifest(config, messages):
    fw_details = dict()
    key = "heat_cfn"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "heat cfn"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8000']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_HEAT_CFN_RULES'] = fw_details
