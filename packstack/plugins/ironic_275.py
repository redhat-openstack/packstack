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
Installs and configures Ironic
"""

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------------ Ironic Packstack Plugin initialization ------------------

PLUGIN_NAME = "OS-Ironic"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    ironic_params = [
        {"CONF_NAME": "CONFIG_IRONIC_DB_PW",
         "CMD_OPTION": "os-ironic-db-passwd",
         "PROMPT": "Enter the password for the Ironic DB user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_KS_PW",
         "CMD_OPTION": "os-ironic-ks-passwd",
         "PROMPT": "Enter the password for Ironic Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, ironic_params, sectioned=False)
    ironic_group = {"GROUP_NAME": "IRONIC",
                    "DESCRIPTION": "Ironic Options",
                    "PRE_CONDITION": "CONFIG_IRONIC_INSTALL",
                    "PRE_CONDITION_MATCH": "y",
                    "POST_CONDITION": False,
                    "POST_CONDITION_MATCH": True}

    controller.addGroup(ironic_group, ironic_params)


def initSequences(controller):
    if controller.CONF['CONFIG_IRONIC_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Preparing Ironic entries',
         'functions': [create_manifest]},
    ]

    controller.addSequence("Installing OpenStack Ironic", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        ssl_cert_file = config['CONFIG_IRONIC_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_ironic.crt'
        )
        ssl_key_file = config['CONFIG_IRONIC_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_ironic.key'
        )
        service = 'ironic'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    key = "ironic-api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "ironic-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['6385']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_IRONIC_API_RULES'] = fw_details
