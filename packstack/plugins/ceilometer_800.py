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
from packstack.installer.utils import split_hosts

from packstack.modules.documentation import update_params_usage
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import getManifestTemplate
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

            {"CONF_NAME": "CONFIG_CEILOMETER_METERING_BACKEND",
             "CMD_OPTION": "ceilometer-metering-backend",
             "PROMPT": "Enter the metering backend to use",
             "OPTION_LIST": ['database', 'gnocchi'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'database',
             "MASK_INPUT": False,
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "MONGODB": [
            {"CMD_OPTION": "mongodb-host",
             "PROMPT": "Enter the host for the MongoDB server",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_MONGODB_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
        "REDIS": [
            {"CMD_OPTION": "redis-master-host",
             "PROMPT": "Enter the host for the Redis master server",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_MASTER_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ["CONFIG_REDIS_HOST"]},
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
            {"CMD_OPTION": "redis-ha",
             "PROMPT": "Should redis try to use HA?",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_HA",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-slaves",
             "PROMPT": "Enter the host for the redis slave servers",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ssh],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_SLAVE_HOSTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-sentinels",
             "PROMPT": "Enter the host for the redis sentinel servers",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ssh],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_SENTINEL_HOSTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-sentinel-contact",
             "PROMPT":
                 "Enter the IP address of the coordination redis sentinel",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_SENTINEL_CONTACT_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-sentinel-port",
             "PROMPT": ("Enter the port on which the redis sentinel servers"
                        " listen"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_port],
             "DEFAULT_VALUE": 26379,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_SENTINEL_PORT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-sentinel-quorum",
             "PROMPT": (
                 "Enter the quorum value for the redis sentinel servers"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": 2,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_SENTINEL_QUORUM",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "redis-sentinel-master-name",
             "PROMPT": (
                 "Enter the logical name of the master server"),
             "OPTION_LIST": [r'[a-z]+'],
             "VALIDATORS": [validators.validate_regexp],
             "DEFAULT_VALUE": 'mymaster',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_REDIS_MASTER_NAME",
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

        {"GROUP_NAME": "MONGODB",
         "DESCRIPTION": "MONGODB Config parameters",
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

    steps = [{'title': 'Adding MongoDB manifest entries',
              'functions': [create_mongodb_manifest]},
             {'title': 'Adding Redis manifest entries',
              'functions': [create_redis_manifest]},
             {'title': 'Adding Ceilometer manifest entries',
              'functions': [create_manifest]},
             {'title': 'Adding Ceilometer Keystone manifest entries',
              'functions': [create_keystone_manifest]}]
    controller.addSequence("Installing OpenStack Ceilometer", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    manifestfile = "%s_ceilometer.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "ceilometer"))
    manifestdata += getManifestTemplate("ceilometer")
    if config['CONFIG_CEILOMETER_SERVICE_NAME'] == 'httpd':
        manifestdata += getManifestTemplate("apache_ports")

    if config['CONFIG_CEILOMETER_COORDINATION_BACKEND'] == 'redis':
        # Determine if we need to configure multiple sentinel hosts as
        # fallbacks for use in coordination url.
        sentinel_hosts = split_hosts(config['CONFIG_REDIS_SENTINEL_HOSTS'])
        sentinel_port = config['CONFIG_REDIS_SENTINEL_PORT']
        sentinel_host = config['CONFIG_REDIS_SENTINEL_CONTACT_HOST']
        if config['CONFIG_IP_VERSION'] == 'ipv6':
            config['CONFIG_REDIS_SENTINEL_CONTACT_HOST_URL'] = "[%s]" % (
                sentinel_host)
        else:
            config['CONFIG_REDIS_SENTINEL_CONTACT_HOST_URL'] = sentinel_host

        sentinel_contact = config['CONFIG_REDIS_SENTINEL_CONTACT_HOST']
        if len(sentinel_hosts) > 1:
            sentinel_format = 'sentinel_fallback=%s:%s'
            if config['CONFIG_IP_VERSION'] == 'ipv6':
                sentinel_format = 'sentinel_fallback=[%s]:%s'

            sentinel_fallbacks = '&'.join([sentinel_format %
                                          (host, sentinel_port)
                                          for host in sentinel_hosts
                                          if host != sentinel_contact])
        else:
            sentinel_fallbacks = ''
        config['CONFIG_REDIS_SENTINEL_FALLBACKS'] = sentinel_fallbacks

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
    key = "ceilometer_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "ceilometer-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8777']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_CEILOMETER_RULES'] = fw_details
    manifestdata += createFirewallResources('FIREWALL_CEILOMETER_RULES')

    # Add a template that creates a group for nova because the ceilometer
    # class needs it
    if config['CONFIG_NOVA_INSTALL'] == 'n':
        manifestdata += getManifestTemplate("ceilometer_nova_disabled")
    appendManifestFile(manifestfile, manifestdata, 'ceilometer')


def create_mongodb_manifest(config, messages):
    host = config['CONFIG_MONGODB_HOST']
    if config['CONFIG_IP_VERSION'] == 'ipv6':
        config['CONFIG_MONGODB_HOST_URL'] = "[%s]" % host
    else:
        config['CONFIG_MONGODB_HOST_URL'] = host
    manifestfile = "%s_mongodb.pp" % config['CONFIG_MONGODB_HOST']
    manifestdata = getManifestTemplate("mongodb")

    fw_details = dict()
    key = "mongodb_server"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "%s" % config['CONFIG_CONTROLLER_HOST']
    fw_details[key]['service_name'] = "mongodb-server"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['27017']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MONGODB_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_MONGODB_RULES')
    appendManifestFile(manifestfile, manifestdata, 'pre')


def create_redis_manifest(config, messages):
    if config['CONFIG_CEILOMETER_COORDINATION_BACKEND'] == 'redis':
        redis_master_host = config['CONFIG_REDIS_MASTER_HOST']
        if config['CONFIG_IP_VERSION'] == 'ipv6':
            config['CONFIG_REDIS_MASTER_HOST_URL'] = "[%s]" % redis_master_host
        else:
            config['CONFIG_REDIS_MASTER_HOST_URL'] = redis_master_host

        # master
        manifestfile = "%s_redis.pp" % config['CONFIG_REDIS_MASTER_HOST']
        manifestdata = getManifestTemplate("redis.pp")

        master_clients = set([config['CONFIG_CONTROLLER_HOST']]).union(
            split_hosts(config['CONFIG_REDIS_SLAVE_HOSTS'])).union(
            split_hosts(config['CONFIG_REDIS_SENTINEL_HOSTS']))
        config['FIREWALL_REDIS_RULES'] = _create_redis_firewall_rules(
            master_clients, config['CONFIG_REDIS_PORT'])

        manifestdata += createFirewallResources('FIREWALL_REDIS_RULES')
        appendManifestFile(manifestfile, manifestdata, 'pre')

        # slaves
        if config['CONFIG_REDIS_HA'] == 'y':
            for slave in split_hosts(config['CONFIG_REDIS_SLAVE_HOSTS']):
                config['CONFIG_REDIS_HOST'] = slave
                manifestfile = "%s_redis_slave.pp" % slave
                manifestdata = getManifestTemplate("redis_slave.pp")

                slave_clients = set([config['CONFIG_CONTROLLER_HOST']]).union(
                    split_hosts(config['CONFIG_REDIS_SLAVE_HOSTS'])).union(
                        split_hosts(config['CONFIG_REDIS_SENTINEL_HOSTS']))
                config['FIREWALL_REDIS_SLAVE_RULES'] = (
                    _create_redis_firewall_rules(
                        slave_clients, config['CONFIG_REDIS_PORT']))

                manifestdata += createFirewallResources(
                    'FIREWALL_REDIS_SLAVE_RULES')
                appendManifestFile(manifestfile, manifestdata, 'pre')

        # sentinels
        if config['CONFIG_REDIS_HA'] == 'y':
            for sentinel in split_hosts(config['CONFIG_REDIS_SENTINEL_HOSTS']):
                manifestfile = "%s_redis_sentinel.pp" % sentinel
                manifestdata = getManifestTemplate("redis_sentinel.pp")

                config['FIREWALL_SENTINEL_RULES'] = (
                    _create_redis_firewall_rules(
                        split_hosts(config['CONFIG_REDIS_SENTINEL_HOSTS']),
                        config['CONFIG_REDIS_SENTINEL_PORT']))

                manifestdata += createFirewallResources(
                    'FIREWALL_SENTINEL_RULES')
                appendManifestFile(manifestfile, manifestdata, 'pre')


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_ceilometer")
    appendManifestFile(manifestfile, manifestdata)


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
