# -*- coding: utf-8 -*-

"""
Installs and configures MariaDB
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer.utils import split_hosts
from packstack.modules.common import filtered_hosts

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "MariaDB"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "mariadb-host",
         "USAGE": ("The IP address of the server on which to install MariaDB "
                   "or IP address of DB server to use if MariaDB "
                   "installation was not selected"),
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
    group = {"GROUP_NAME": "MARIADB",
             "DESCRIPTION": "MariaDB Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    mariadbsteps = [
        {'title': 'Adding MariaDB manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing MariaDB", [], [], mariadbsteps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_MARIADB_INSTALL'] == 'y':
        suffix = 'install'
        host = config['CONFIG_MARIADB_HOST']
    else:
        suffix = 'noinstall'
        host = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_mariadb.pp" % host
    manifestdata = [getManifestTemplate('mariadb_%s.pp' % suffix)]

    def append_for(module, suffix):
        # Modules have to be appended to the existing mysql.pp
        # otherwise pp will fail for some of them saying that
        # Mysql::Config definition is missing.
        template = "mariadb_%s_%s.pp" % (module, suffix)
        manifestdata.append(getManifestTemplate(template))

    append_for("keystone", suffix)
    for mod in ['nova', 'cinder', 'glance', 'neutron', 'heat']:
        if config['CONFIG_%s_INSTALL' % mod.upper()] == 'y':
            append_for(mod, suffix)

    hosts = filtered_hosts(config, exclude=False, dbhost=True)

    fw_details = dict()
    for host in hosts:
        key = "mariadb_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "mariadb"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['3306']
        fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MARIADB_RULES'] = fw_details

    manifestdata.append(createFirewallResources('FIREWALL_MARIADB_RULES'))
    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')
