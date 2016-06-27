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
Installs and configures Trove
"""

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------------ Trove Packstack Plugin initialization ------------------

PLUGIN_NAME = "OS-Trove"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


# NOVA_USER, NOVA_TENANT, NOVA_PW

def process_trove_nova_pw(param, param_name, config=None):
    if (param == 'PW_PLACEHOLDER' and
            config['CONFIG_TROVE_NOVA_USER'] == 'trove'):
        return config['CONFIG_TROVE_KS_PW']
    else:
        return param


def initConfig(controller):
    parameters = [
        {"CONF_NAME": "CONFIG_TROVE_DB_PW",
         "CMD_OPTION": "trove-db-passwd",
         "PROMPT": "Enter the password to use for Trove to access the DB",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_TROVE_KS_PW",
         "CMD_OPTION": "trove-ks-passwd",
         "PROMPT": "Enter the password for Trove Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_TROVE_NOVA_USER",
         "CMD_OPTION": "trove-nova-user",
         "PROMPT": "Enter the user for Trove to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "trove",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_TROVE_NOVA_TENANT",
         "CMD_OPTION": "trove-nova-tenant",
         "PROMPT": "Enter the tenant for Trove to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "services",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_TROVE_NOVA_PW",
         "CMD_OPTION": "trove-nova-passwd",
         "PROMPT": "Enter the password for Trove to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",  # default is trove pass
         "PROCESSORS": [process_trove_nova_pw],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, parameters, sectioned=False)
    group = {"GROUP_NAME": "Trove",
             "DESCRIPTION": "Trove config parameters",
             "PRE_CONDITION": "CONFIG_TROVE_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}

    controller.addGroup(group, parameters)


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_TROVE_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Preparing Trove entries',
         'functions': [create_manifest]}
    ]

    controller.addSequence("Installing Trove", [], [], steps)


# ------------------------ step functions --------------------------
def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_cert_file = config['CONFIG_TROVE_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_trove.crt'
        )
        ssl_key_file = config['CONFIG_TROVE_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_trove.key'
        )
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        service = 'trove'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    if (config['CONFIG_TROVE_NOVA_USER'] == 'trove' and
            config['CONFIG_TROVE_NOVA_PW'] == ''):
        config['CONFIG_TROVE_NOVA_PW'] = config['CONFIG_TROVE_KS_PW']

    fw_details = dict()
    key = "trove"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "trove api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8779']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_TROVE_API_RULES'] = fw_details
