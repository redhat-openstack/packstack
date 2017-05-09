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
Installs and configures MariaDB
"""

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.common import filtered_hosts
from packstack.modules.documentation import update_params_usage

# ------------- MariaDB Packstack Plugin Initialization --------------

PLUGIN_NAME = "MariaDB"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "mariadb-host",
         "PROMPT": "Enter the IP address of the MariaDB server",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_ssh],
         "DEFAULT_VALUE": utils.get_localhost_ip(),
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_MARIADB_HOST",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_MYSQL_HOST']},

        {"CMD_OPTION": "mariadb-user",
         "USAGE": "Username for the MariaDB admin user",
         "PROMPT": "Enter the username for the MariaDB admin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "root",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_MARIADB_USER",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_MYSQL_USER']},

        {"CMD_OPTION": "mariadb-pw",
         "USAGE": "Password for the MariaDB admin user",
         "PROMPT": "Enter the password for the MariaDB admin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_MARIADB_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_MYSQL_PW']},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "MARIADB",
             "DESCRIPTION": "MariaDB Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    mariadbsteps = [
        {'title': 'Preparing MariaDB entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing MariaDB", [], [], mariadbsteps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_MARIADB_INSTALL'] == 'y':
        host = config['CONFIG_CONTROLLER_HOST']
    else:
        host = config['CONFIG_MARIADB_HOST']

    if config['CONFIG_IP_VERSION'] == 'ipv6':
        config['CONFIG_MARIADB_HOST_URL'] = "[%s]" % host
    else:
        config['CONFIG_MARIADB_HOST_URL'] = host

    fw_details = dict()
    for host in filtered_hosts(config, exclude=False, dbhost=True):
        key = "mariadb_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "mariadb"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['3306']
        fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MARIADB_RULES'] = fw_details
