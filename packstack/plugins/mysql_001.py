"""
Installs and configures MySQL
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-MySQL"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding MySQL OpenStack configuration")
    paramsList = [
                  {"CMD_OPTION"      : "mysql-host",
                   "USAGE"           : "The IP address of the server on which to install MySQL",
                   "PROMPT"          : "Enter the IP address of the MySQL server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-user",
                   "USAGE"           : "Username for the MySQL admin user",
                   "PROMPT"          : "Enter the username for the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "root",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_MYSQL_USER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-pw",
                   "USAGE"           : "Password for the MySQL admin user",
                   "PROMPT"          : "Enter the password for the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "MYSQL",
                  "DESCRIPTION"           : "MySQL Config parameters",
                  "PRE_CONDITION"         : lambda x: 'yes',
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    mysqlsteps = [
             {'title': 'Adding MySQL manifest entries',
              'functions':[createmanifest]}
    ]
    controller.addSequence("Installing MySQL", [], [], mysqlsteps)


def createmanifest(config):
    if config['CONFIG_MYSQL_INSTALL'] == 'y':
        install = True
        suffix = 'install'
    else:
        install = False
        suffix = 'noinstall'

    # In case we are not installing MySQL server, mysql* manifests have
    # to be run from Keystone host
    host = install and config['CONFIG_MYSQL_HOST'] \
                    or config['CONFIG_KEYSTONE_HOST']
    manifestfile = "%s_mysql.pp" % host
    manifestdata = [getManifestTemplate('mysql_%s.pp' % suffix)]

    def append_for(module, suffix):
        # Modules have to be appended to the existing mysql.pp
        # otherwise pp will fail for some of them saying that
        # Mysql::Config definition is missing.
        template = "mysql_%s_%s.pp" % (module, suffix)
        manifestdata.append(getManifestTemplate(template))

    append_for("keystone", suffix)
    for mod in ['nova', 'cinder', 'glance', 'neutron']:
        if config['CONFIG_%s_INSTALL' % mod.upper()] == 'y':
            append_for(mod, suffix)

    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')
