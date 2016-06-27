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
Installs and configures Glance
"""

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Glance Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Glance"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "glance-db-passwd",
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
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
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
        {'title': 'Preparing Glance entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Glance", [], [], glancesteps)


# ------------------------- helper functions -------------------------

def process_backend(value, param_name, config):
    if value == 'swift' and config['CONFIG_SWIFT_INSTALL'] != 'y':
        return 'file'
    return value


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_host = config['CONFIG_STORAGE_HOST']
        ssl_cert_file = config['CONFIG_GLANCE_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_glance.crt'
        )
        ssl_key_file = config['CONFIG_GLANCE_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_glance.key'
        )
        service = 'glance'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    key = "glance_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "glance"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['9292']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_GLANCE_RULES'] = fw_details
