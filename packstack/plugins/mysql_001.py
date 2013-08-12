"""
Installs and configures MySQL
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import basedefs
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
    host = controller.CONF['CONFIG_MYSQL_HOST']
    manifestfile = "%s_mysql.pp" % host
    manifestdata = [getManifestTemplate("mysql.pp")]

    def append_for(module):
        # Modules have be appended to the existing mysql.pp
        # otherwise pp will fail for some of them saying that
        # Mysql::Config definition is missing.
        manifestdata.append(getManifestTemplate("mysql_%s.pp" % module))

    if controller.CONF['CONFIG_NOVA_INSTALL'] == "y":
        append_for("nova")
    if controller.CONF['CONFIG_CINDER_INSTALL'] == "y":
        append_for("cinder")
    if controller.CONF['CONFIG_GLANCE_INSTALL'] == "y":
        append_for("glance")
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] == 'y':
        append_for("neutron")

    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')
