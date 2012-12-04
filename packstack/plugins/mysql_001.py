"""
Installs and configures MySQL
"""

import logging

import packstack.installer.engine_validators as validate
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-MySQL"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding MySQL Openstack configuration")
    paramsList = [
                  {"CMD_OPTION"      : "mysql-host",
                   "USAGE"           : "The IP address of the server on which to install MySQL",
                   "PROMPT"          : "The IP address of the server on which to install MySQL",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-user",
                   "USAGE"           : "Username of the MySQL admin user",
                   "PROMPT"          : "Username of the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "root",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_MYSQL_USER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-pw",
                   "USAGE"           : "Password for the MySQL admin user",
                   "PROMPT"          : "Password for the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : lambda a,b: True,
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "MYSQL",
                  "DESCRIPTION"           : "MySQL Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    mysqlsteps = [
             {'title': 'Create MySQL Manifest',
              'functions':[createmanifest]}
    ]
    controller.addSequence("Installing MySQL", [], [], mysqlsteps)

def createmanifest():
    manifestfile = "%s_mysql.pp"%controller.CONF['CONFIG_MYSQL_HOST']
    manifestdata = getManifestTemplate("mysql.pp")
    appendManifestFile(manifestfile, manifestdata, 'pre')

