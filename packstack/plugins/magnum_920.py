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
Installs and configures Magnum
"""

from packstack.installer import basedefs
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Magnum Packstack Plugin Initialization --------------
PLUGIN_NAME = "OS-Magnum"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    magnum_params = {
        "MAGNUM": [
            {"CMD_OPTION": "magnum-db-passwd",
             "PROMPT": "Enter the password for the Magnum DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MAGNUM_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "magnum-ks-passwd",
             "PROMPT": "Enter the password for the Magnum Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MAGNUM_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
        ]

    }
    update_params_usage(basedefs.PACKSTACK_DOC, magnum_params)

    magnum_groups = [
        {"GROUP_NAME": "MAGNUM",
         "DESCRIPTION": "Magnum Options",
         "PRE_CONDITION": "CONFIG_MAGNUM_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in magnum_groups:
        params = magnum_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_MAGNUM_INSTALL'] != 'y':
        return

    magnum_steps = [
        {'title': 'Adding Magnum manifest entries',
         'functions': [create_all_manifest]},
    ]

    controller.addSequence("Installing OpenStack Magnum", [], [],
                           magnum_steps)


# ------------------------- helper functions -------------------------

# ------------------------ Step Functions ----------------------------
def create_all_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_cert_file = config['CONFIG_MAGNUM_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_magnum.crt'
        )
        ssl_key_file = config['CONFIG_MAGNUM_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_magnum.key'
        )
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        service = 'magnum'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    key = "magnum"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "magnum api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['9511']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MAGNUM_API_RULES'] = fw_details
