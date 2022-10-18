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
Installs and configures Ceilometer
"""

import uuid

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Ceilometer Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Ceilometer"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    ceilometer_params = {
        "CEILOMETER": [
            {"CONF_NAME": "CONFIG_CEILOMETER_SECRET",
             "CMD_OPTION": "ceilometer-secret",
             "PROMPT": "Enter the Ceilometer secret key",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": uuid.uuid4().hex[:16],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": True,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_CEILOMETER_KS_PW",
             "CMD_OPTION": "ceilometer-ks-passwd",
             "PROMPT": "Enter the password for the Ceilometer Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "ceilometer-service-name",
             "PROMPT": "Enter the Ceilometer service name.",
             "OPTION_LIST": ['ceilometer', 'httpd'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "httpd",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_CEILOMETER_SERVICE_NAME',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_CEILOMETER_COORDINATION_BACKEND",
             "CMD_OPTION": "ceilometer-coordination-backend",
             "PROMPT": "Enter the coordination driver",
             "OPTION_LIST": ['redis', 'none'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'redis',
             "MASK_INPUT": False,
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_ENABLE_CEILOMETER_MIDDLEWARE",
             "CMD_OPTION": "enable-ceilometer-middleware",
             "PROMPT": ("Enable ceilometer middleware in swift proxy"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "REDIS": [
            {"CMD_OPTION": "redis-host",
             "PROMPT": "Enter the host for the Redis server",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ["CONFIG_REDIS_MASTER_HOST"]},
            {"CMD_OPTION": "redis-port",
             "PROMPT": "Enter the port of the redis server(s)",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_port],
             "DEFAULT_VALUE": 6379,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_PORT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
    }
    update_params_usage(basedefs.PACKSTACK_DOC, ceilometer_params)

    ceilometer_groups = [
        {"GROUP_NAME": "CEILOMETER",
         "DESCRIPTION": "Ceilometer Config parameters",
         "PRE_CONDITION": "CONFIG_CEILOMETER_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "REDIS",
         "DESCRIPTION": "Redis Config parameters",
         "PRE_CONDITION": "CONFIG_CEILOMETER_COORDINATION_BACKEND",
         "PRE_CONDITION_MATCH": "redis",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in ceilometer_groups:
        paramList = ceilometer_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def initSequences(controller):
    if controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y':
        return

    steps = [{'title': 'Preparing Redis entries',
              'functions': [create_redis_manifest]},
             {'title': 'Preparing Ceilometer entries',
              'functions': [create_manifest]}]
    controller.addSequence("Installing OpenStack Ceilometer", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_cert_file = config['CONFIG_CEILOMETER_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_ceilometer.crt'
        )
        ssl_key_file = config['CONFIG_CEILOMETER_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_ceilometer.key'
        )
        ssl_host = config['CONFIG_CONTROLLER_HOST']
        service = 'ceilometer'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    # NOTE(tkajinam): ceilometer has no API service now
    config['FIREWALL_CEILOMETER_RULES'] = fw_details


def create_redis_manifest(config, messages):
    if config['CONFIG_CEILOMETER_COORDINATION_BACKEND'] == 'redis':
        redis_host = config['CONFIG_REDIS_HOST']
        if config['CONFIG_IP_VERSION'] == 'ipv6':
            config['CONFIG_REDIS_HOST_URL'] = "[%s]" % redis_host
        else:
            config['CONFIG_REDIS_HOST_URL'] = redis_host

        # master
        master_clients = set([config['CONFIG_CONTROLLER_HOST']])
        config['FIREWALL_REDIS_RULES'] = _create_redis_firewall_rules(
            master_clients, config['CONFIG_REDIS_PORT'])


# ------------------------- helper functions -------------------------

def _create_redis_firewall_rules(hosts, port):
    fw_details = dict()
    for host in hosts:
        key = "redis service from %s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "redis service"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = port
        fw_details[key]['proto'] = "tcp"
    return fw_details
