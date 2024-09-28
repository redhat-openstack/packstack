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
Installs and configures AMQP
"""

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.common import filtered_hosts
from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- AMQP Packstack Plugin Initialization --------------

PLUGIN_NAME = "AMQP"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "amqp-backend",
         "PROMPT": "Set the AMQP service backend",
         "OPTION_LIST": ["rabbitmq"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "rabbitmq",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_BACKEND",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_AMQP_SERVER']},

        {"CMD_OPTION": "amqp-host",
         "PROMPT": "Enter the host for the AMQP service",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_ssh],
         "DEFAULT_VALUE": utils.get_localhost_ip(),
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_HOST",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-enable-ssl",
         "PROMPT": "Enable SSL for the AMQP service?",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_ENABLE_SSL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-enable-auth",
         "PROMPT": "Enable Authentication for the AMQP service?",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_ENABLE_AUTH",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "AMQP",
             "DESCRIPTION": "AMQP Config parameters",
             "PRE_CONDITION": False,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    params = [
        {"CMD_OPTION": "amqp-auth-user",
         "PROMPT": "Enter the user for amqp authentication",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "amqp_user",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_AUTH_USER",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-auth-password",
         "PROMPT": "Enter the password for user authentication",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_AUTH_PASSWORD",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "AMQPAUTH",
             "DESCRIPTION": "AMQP Config Authentication parameters",
             "PRE_CONDITION": "CONFIG_AMQP_ENABLE_AUTH",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    amqpsteps = [
        {'title': 'Preparing AMQP entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing AMQP", [], [], amqpsteps)


# ------------------------ step functions -------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        config['CONFIG_AMQP_SSL_ENABLED'] = True
        config['CONFIG_AMQP_PROTOCOL'] = 'ssl'
        config['CONFIG_AMQP_CLIENTS_PORT'] = "5671"
        amqp_host = config['CONFIG_AMQP_HOST']
        service = 'AMQP'
        ssl_key_file = '/etc/pki/tls/private/ssl_amqp.key'
        ssl_cert_file = '/etc/pki/tls/certs/ssl_amqp.crt'
        config['CONFIG_AMQP_SSL_CACERT_FILE'] = config['CONFIG_SSL_CACERT']
        generate_ssl_cert(config, amqp_host, service, ssl_key_file,
                          ssl_cert_file)
    else:
        # Set default values
        config['CONFIG_AMQP_CLIENTS_PORT'] = "5672"
        config['CONFIG_AMQP_SSL_ENABLED'] = False
        config['CONFIG_AMQP_PROTOCOL'] = 'tcp'

    if config['CONFIG_AMQP_ENABLE_AUTH'] == 'n':
        config['CONFIG_AMQP_AUTH_PASSWORD'] = 'guest'
        config['CONFIG_AMQP_AUTH_USER'] = 'guest'

    if config['CONFIG_IP_VERSION'] == 'ipv6':
        config['CONFIG_AMQP_HOST_URL'] = "[%s]" % config['CONFIG_AMQP_HOST']
    else:
        config['CONFIG_AMQP_HOST_URL'] = config['CONFIG_AMQP_HOST']

    fw_details = dict()
    # All hosts should be able to talk to amqp
    for host in filtered_hosts(config, exclude=False):
        key = "amqp_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "amqp"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['5671', '5672']
        fw_details[key]['proto'] = "tcp"
    config['FIREWALL_AMQP_RULES'] = fw_details
