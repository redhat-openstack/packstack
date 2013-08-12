"""
Plugin responsible for setting OpenStack global options
"""

import logging
import os
import uuid

from packstack.installer import exceptions
from packstack.installer import utils
from packstack.installer import validators
from packstack.modules.ospluginutils import gethostlist,\
                                            getManifestTemplate, \
                                            appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-PRESCRIPT"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "os-glance-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Image Service (Glance)",
                   "PROMPT"          : "Should Packstack install OpenStack Image Service (Glance)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-cinder-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Block Storage (Cinder)",
                   "PROMPT"          : "Should Packstack install OpenStack Block Storage (Cinder) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-nova-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Compute (Nova)",
                   "PROMPT"          : "Should Packstack install OpenStack Compute (Nova) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-neutron-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Networking (Neutron)",
                   "PROMPT"          : "Should Packstack install OpenStack Networking (Neutron) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NEUTRON_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-horizon-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Dashboard (Horizon)",
                   "PROMPT"          : "Should Packstack install OpenStack Dashboard (Horizon)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_HORIZON_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Object Storage (Swift)",
                   "PROMPT"          : "Should Packstack install OpenStack Object Storage (Swift)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SWIFT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-client-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin \"rc\" file will also be installed",
                   "PROMPT"          : "Should Packstack install OpenStack client tools",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CLIENT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "ntp-severs",
                   "USAGE"           : "Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances.",
                   "PROMPT"          : "Enter a comma separated list of NTP server(s). Leave plain if Packstack should not install ntpd on instances.",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : '',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NTP_SERVERS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nagios-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Nagios to monitor openstack hosts",
                   "PROMPT"          : "Should Packstack install Nagios to monitor openstack hosts",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : 'n',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NAGIOS_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "exclude-servers",
                   "USAGE"           : "Comma separated list of servers to be excluded from installation in case you are running Packstack the second time with the same answer file and don't want Packstack to touch these servers. Leave plain if you don't need to exclude any server.",
                   "PROMPT"          : "Enter a comma separated list of server(s) to be excluded. Leave plain if you don't need to exclude any server.",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : '',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "EXCLUDE_SERVERS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "GLOBAL",
                  "DESCRIPTION"           : "Global Options",
                  "PRE_CONDITION"         : lambda x: 'yes',
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    osclientsteps = [
             {'title': 'Adding pre install manifest entries', 'functions':[createmanifest]},
    ]
    controller.addSequence("Running pre install scripts", [], [], osclientsteps)

    if controller.CONF['CONFIG_NTP_SERVERS']:
        ntp_step = [{'functions': [create_ntp_manifest],
                     'title': 'Installing time synchronization via NTP'}]
        controller.addSequence('Installing time synchronization via NTP', [], [], ntp_step)
    else:
        controller.MESSAGES.append('Time synchronization installation '
                                   'was skipped. Please note that '
                                   'unsynchronized time on server '
                                   'instances might be problem for '
                                   'some OpenStack components.')

def createmanifest(config):
    for hostname in gethostlist(controller.CONF):
        manifestfile = "%s_prescript.pp" % hostname
        manifestdata = getManifestTemplate("prescript.pp")
        appendManifestFile(manifestfile, manifestdata)

def create_ntp_manifest(config):
    srvlist = [i.strip()
               for i in config['CONFIG_NTP_SERVERS'].split(',')
               if i.strip()]
    config['CONFIG_NTP_SERVERS'] = ' '.join(srvlist)

    definiton = '\n'.join(['server %s' % i for i in srvlist])
    config['CONFIG_NTP_SERVER_DEF'] = '%s\n' % definiton

    marker = uuid.uuid4().hex[:16]
    for hostname in gethostlist(config):
        manifestdata = getManifestTemplate('ntpd.pp')
        appendManifestFile('%s_ntpd.pp' % hostname,
                           manifestdata,
                           marker=marker)
