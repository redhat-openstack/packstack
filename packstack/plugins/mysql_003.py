# -*- coding: utf-8 -*-

"""
Installs and configures MySQL
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import utils
from packstack.installer.utils import split_hosts
from packstack.modules.common import filtered_hosts

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "MySQL"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "mysql-host",
         "USAGE": ("The IP address of the server on which to install MySQL or "
                   "IP address of DB server to use if MySQL installation was "
                   "not selected"),
         "PROMPT": "Enter the IP address of the MySQL server",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_ssh],
         "DEFAULT_VALUE": utils.get_localhost_ip(),
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_MYSQL_HOST",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "mysql-user",
         "USAGE": "Username for the MySQL admin user",
         "PROMPT": "Enter the username for the MySQL admin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "root",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_MYSQL_USER",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "mysql-pw",
         "USAGE": "Password for the MySQL admin user",
         "PROMPT": "Enter the password for the MySQL admin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_MYSQL_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "MYSQL",
             "DESCRIPTION": "MySQL Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    mysqlsteps = [
        {'title': 'Adding MySQL manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing MySQL", [], [], mysqlsteps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    if config['CONFIG_MYSQL_INSTALL'] == 'y':
        suffix = 'install'
        host = config['CONFIG_MYSQL_HOST']
    else:
        suffix = 'noinstall'
        host = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_mysql.pp" % host
    manifestdata = [getManifestTemplate('mysql_%s.pp' % suffix)]

    def append_for(module, suffix):
        # Modules have to be appended to the existing mysql.pp
        # otherwise pp will fail for some of them saying that
        # Mysql::Config definition is missing.
        template = "mysql_%s_%s.pp" % (module, suffix)
        manifestdata.append(getManifestTemplate(template))

    append_for("keystone", suffix)
    for mod in ['nova', 'cinder', 'glance', 'neutron', 'heat']:
        if config['CONFIG_%s_INSTALL' % mod.upper()] == 'y':
            append_for(mod, suffix)

    hosts = filtered_hosts(config, exclude=False, dbhost=True)

    config['FIREWALL_SERVICE_NAME'] = "mysql"
    config['FIREWALL_PORTS'] = "'3306'"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    for host in hosts:
        config['FIREWALL_ALLOWED'] = "'%s'" % host
        config['FIREWALL_SERVICE_ID'] = "mysql_%s" % host
        manifestdata.append(getManifestTemplate("firewall.pp"))

    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')
