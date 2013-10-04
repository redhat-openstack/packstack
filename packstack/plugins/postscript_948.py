"""
Installs and configures an OpenStack Client
"""

import logging

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-POSTSCRIPT"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Executing post run scripts")


    groupDict = {"GROUP_NAME"            : "POSTSCRIPT",
                 "DESCRIPTION"           : "POSTSCRIPT Config parameters",
                 "PRE_CONDITION"         : lambda x: 'yes',
                 "PRE_CONDITION_MATCH"   : "yes",
                 "POST_CONDITION"        : False,
                 "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, [])


def initSequences(controller):
    osclientsteps = [
             {'title': 'Adding post install manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Running post install scripts", [], [], osclientsteps)


def createmanifest(config):
    for hostname in filtered_hosts(config):
        manifestfile = "%s_postscript.pp" % hostname
        manifestdata = getManifestTemplate("postscript.pp")
        appendManifestFile(manifestfile, manifestdata, 'postscript')
        if config.get("CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE") != 'n':
            config['EXT_BRIDGE_VAR'] = config['CONFIG_NEUTRON_L3_EXT_BRIDGE'].replace('-','_')
            manifestdata = getManifestTemplate("persist_ovs_bridge.pp")
            appendManifestFile(manifestfile, manifestdata, 'postscript')
