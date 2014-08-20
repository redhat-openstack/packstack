"""
Installs and configures Glance
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer.utils import split_hosts

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Glance"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Glance configuration")
    paramsList = [
                  {"CMD_OPTION"      : "glance-host",
                   "USAGE"           : "The IP address of the server on which to install Glance",
                   "PROMPT"          : "Enter the IP address of the Glance server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_GLANCE_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "glance-db-passwd",
                   "USAGE"           : "The password to use for the Glance to access DB",
                   "PROMPT"          : "Enter the password for the Glance DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "glance-ks-passwd",
                   "USAGE"           : "The password to use for the Glance to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Glance Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "GLANCE",
                  "DESCRIPTION"           : "Glance Config parameters",
                  "PRE_CONDITION"         : "CONFIG_GLANCE_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    conf = controller.CONF
    if conf['CONFIG_GLANCE_INSTALL'] != 'y':
        if conf['CONFIG_NOVA_INSTALL'] == 'y':
            raise RuntimeError('Glance is required to install Nova properly. '
                               'Please set CONFIG_GLANCE_INSTALL=y')
        return

    glancesteps = [
             {'title': 'Adding Glance Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Glance manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Glance", [], [], glancesteps)

def createkeystonemanifest(config):
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_glance.pp")
    appendManifestFile(manifestfile, manifestdata)

def createmanifest(config):
    manifestfile = "%s_glance.pp" % controller.CONF['CONFIG_GLANCE_HOST']
    manifestdata = getManifestTemplate("glance.pp")
    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('glance_ceilometer.pp')

    config['FIREWALL_SERVICE_NAME'] = "glance"
    config['FIREWALL_PORTS'] = "'9292'"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        for host in split_hosts(config['CONFIG_NOVA_COMPUTE_HOSTS']):
            config['FIREWALL_ALLOWED'] = "'%s'" % host
            config['FIREWALL_SERVICE_ID'] = "glance_%s" % host
            manifestdata += getManifestTemplate("firewall.pp")
    else:
        config['FIREWALL_ALLOWED'] = "'ALL'"
        config['FIREWALL_SERVICE_ID'] = "glance_ALL"
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata)
