# -*- coding: utf-8 -*-

"""
Plugin responsible for post-installation configuration
"""

from packstack.installer import utils

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


# ------------- Postscript Packstack Plugin Initialization --------------

PLUGIN_NAME = "Postscript"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    group = {"GROUP_NAME": "POSTSCRIPT",
             "DESCRIPTION": "POSTSCRIPT Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, [])


def initSequences(controller):
    postscript_steps = [
        {'title': 'Adding post install manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Running post install scripts", [], [],
                           postscript_steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    for hostname in filtered_hosts(config):
        manifestfile = "%s_postscript.pp" % hostname
        manifestdata = getManifestTemplate("postscript.pp")
        appendManifestFile(manifestfile, manifestdata, 'postscript')
        # TO-DO: remove this temporary fix for nova-network/neutron
        #        undeterministic behavior
        provision = (
            config.get("CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE") not in
            set(['false', 'n', None])
        )
        if config.get('CONFIG_NEUTRON_INSTALL', 'n') == 'y' and provision:
            fmted = config['CONFIG_NEUTRON_L3_EXT_BRIDGE'].replace('-', '_')
            config['EXT_BRIDGE_VAR'] = fmted
            manifestdata = getManifestTemplate("persist_ovs_bridge.pp")
            appendManifestFile(manifestfile, manifestdata, 'postscript')
