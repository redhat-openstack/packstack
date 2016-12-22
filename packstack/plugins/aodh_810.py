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
Installs and configures Aodh
"""

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Aodh Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Aodh"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    aodh_params = {
        "AODH": [
            {"CONF_NAME": "CONFIG_AODH_KS_PW",
             "CMD_OPTION": "aodh-ks-passwd",
             "PROMPT": "Enter the password for the Aodh Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "aodh-db-passwd",
             "PROMPT": "Enter the password for the aodh DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_AODH_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
        ]
    }

    update_params_usage(basedefs.PACKSTACK_DOC, aodh_params)

    def use_aodh(config):
        return (config['CONFIG_CEILOMETER_INSTALL'] == 'y' and
                config['CONFIG_AODH_INSTALL'] == 'y')

    aodh_groups = [
        {"GROUP_NAME": "AODH",
         "DESCRIPTION": "Aodh Config parameters",
         "PRE_CONDITION": use_aodh,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in aodh_groups:
        paramList = aodh_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def initSequences(controller):
    if (controller.CONF['CONFIG_AODH_INSTALL'] != 'y' or
       controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y'):
        return

    steps = [{'title': 'Preparing Aodh entries',
              'functions': [create_manifest]}]
    controller.addSequence("Installing OpenStack Aodh", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_cert_file = config['CONFIG_AODH_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_aodh.crt'
        )
        ssl_key_file = config['CONFIG_AODH_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_aodh.key'
        )
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        service = 'aodh'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    key = "aodh_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "aodh-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8042']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_AODH_RULES'] = fw_details
