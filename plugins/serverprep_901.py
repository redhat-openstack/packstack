"""
prepare server
"""

import glob
import logging
import os

import engine_validators as validate
import basedefs
import common_utils as utils

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
    for hostname in utils.gethostlist(controller.CONF):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        server = utils.ScriptRunner(hostname)

        server.append("rpm -q epel-release-6-7 || rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-7.noarch.rpm")
        server.execute()

