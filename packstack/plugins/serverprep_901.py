"""
prepare server
"""

import glob
import logging
import os

import packstack.installer.engine_validators as validate
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import gethostlist

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SERVERPREPARE"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding SERVERPREPARE KEY configuration")
    conf_params = {"SERVERPREPARE": [
                  {"CMD_OPTION"      : "use-epel",
                   "USAGE"           : "Install openstack from epel, If set to \"n\" this causes EPEL to be permanently disabled before installing openstack, i.e. you should have alternative openstack repositories in place",
                   "PROMPT"          : "Install openstack from epel, If set to \"n\" this causes EPEL to be permanently disabled before installing openstack, i.e. you should have alternative openstack repositories in place",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_USE_EPEL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
            ]
        }

    conf_groups = [
            { "GROUP_NAME"            : "SERVERPREPARE",
              "DESCRIPTION"           : "Server Prepare Configs ",
              "PRE_CONDITION"         : utils.returnYes,
              "PRE_CONDITION_MATCH"   : "yes",
              "POST_CONDITION"        : False,
              "POST_CONDITION_MATCH"  : True},
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)



def initSequences(controller):
    preparesteps = [
             {'title': 'Installing EPEL', 'functions':[installepel]}
    ]
    controller.addSequence("Prepare Server", [], [], preparesteps)


def installepel():
    for hostname in gethostlist(controller.CONF):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        server = utils.ScriptRunner(hostname)

        # install epel if on rhel
        server.append("grep 'Red Hat Enterprise Linux' /etc/redhat-release && ( rpm -q epel-release-6-7 || rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-7.noarch.rpm ) || echo -n ''")
        server.execute()

