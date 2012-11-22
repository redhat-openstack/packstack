"""
Creates a Sample File
"""

import logging
import os

import engine_validators as validate
import basedefs
import common_utils as utils

# Controller object will be initialized from main flow
controller = None

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Initialising Plugine")
    conf_params = {"SAMPLE": [
                  {"CMD_OPTION"      : "filename",
                   "USAGE"           : "File to create",
                   "PROMPT"          : "File to create",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "/tmp/samplefile.txt",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_FILENAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
            ]
        }

    conf_groups = [
            { "GROUP_NAME"            : "SAMPLE",
              "DESCRIPTION"           : "Sample config group",
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
             {'title': 'Create File', 'functions':[createfile]}
    ]
    controller.addSequence("Creating File", [], [], preparesteps)


def createfile():
    with open(controller.CONF["CONFIG_FILENAME"], "a") as fp:
        fp.write("HELLO WORLD")

