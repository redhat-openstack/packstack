"""
Installs and configures nova compute
"""

import logging
import os
import uuid


import engine_validators as validate
import basedefs
import common_utils as utils
import ospluginutils

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-NOVACOMPUTE"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPET_MANIFEST_DIR      = 'puppet/manifests'
PUPPET_MANIFEST_TEMPLATE = 'puppet/templates/nova_compute.pp'

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Nova Compute configuration")
    paramsList = [
                  {"CMD_OPTION"      : "novacompute-hosts",
                   "USAGE"           : "Hostname of the Nova Compute servers (commma seperated)",
                   "PROMPT"          : "Hostname of the Nova Compute server (commma seperated)",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateMultiPing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVACOMPUTE_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "libvirt-type",
                   "USAGE"           : "Libvirt Type to use",
                   "PROMPT"          : "Libvirt Type to use",
                   "OPTION_LIST"     : ["qemu", "kvm"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "kvm",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_LIBVIRT_TYPE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova compute servers",
                   "PROMPT"          : "Private interface for Flat DHCP on the Nova compute servers",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVACOMPUTE_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NOVACOMPUTE",
                  "DESCRIPTION"           : "Nova Compute Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    novacomputesteps = [
             {'title': 'Creating Nova Compute Manifest', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing Nova Compute", [], [], novacomputesteps)

def createmanifest():
    with open(PUPPET_MANIFEST_TEMPLATE) as fp:
        manifestdata = fp.read()
    manifestdata = manifestdata%controller.CONF

    if not os.path.exists(PUPPET_MANIFEST_DIR):
        os.mkdir(PUPPET_MANIFEST_DIR)

    for host in controller.CONF["CONFIG_NOVACOMPUTE_HOSTS"].split(","):
        manifestfile = os.path.join(PUPPET_MANIFEST_DIR, "%s_nova.pp"%host.strip())
        if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
            controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)

        server = utils.ScriptRunner(host)
        nova_config_options = ospluginutils.NovaConfig()

        if host != controller.CONF["CONFIG_NOVANETWORK_HOST"]:
            nova_config_options.addOption("flat_interface", controller.CONF['CONFIG_NOVACOMPUTE_PRIVIF'])
            validate.r_validateMultiPing(server, controller.CONF['CONFIG_NOVACOMPUTE_PRIVIF'])

        server.execute()

        with open(manifestfile, 'a') as fp:
            fp.write("\n")
            fp.write(manifestdata)
            fp.write("\n" + nova_config_options.getManifestEntry())

