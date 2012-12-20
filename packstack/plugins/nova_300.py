"""
Installs and configures nova
"""

import logging
import os

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile, manifestfiles

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "novaapi-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova API service",
                   "PROMPT"          : "Enter the IP address of the Nova API service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_API_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacert-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Cert service",
                   "PROMPT"          : "Enter the IP address of the Nova Cert service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_CERT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novavncproxy-hosts",
                   "USAGE"           : "The IP address of the server on which to install the Nova VNC proxy",
                   "PROMPT"          : "Enter the IP address of the Nova VNC proxy",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_VNCPROXY_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-hosts",
                   "USAGE"           : "A comma separated list of IP addresses on which to install the Nova Compute services",
                   "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Nova Compute services",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateMultiSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_HOSTS", # TO-DO: Create processor for CSV
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova compute servers",
                   "PROMPT"          : "Enter the Private interface for Flat DHCP on the Nova compute servers",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Network service",
                   "PROMPT"          : "Enter the IP address of the Nova Network service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-pubif",
                   "USAGE"           : "Public interface on the Nova network server",
                   "PROMPT"          : "Enter the Public interface on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth0",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PUBIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova network server",
                   "PROMPT"          : "Enter the Private interface for Flat DHCP on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-fixed-range",
                   "USAGE"           : "IP Range for Flat DHCP",
                   "PROMPT"          : "Enter the IP Range for Flat DHCP",
                   "OPTION_LIST"     : ["^([\d]{1,3}\.){3}[\d]{1,3}/\d\d?$"],
                   "VALIDATION_FUNC" : validate.validateRe,
                   "DEFAULT_VALUE"   : "192.168.32.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FIXEDRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-floating-range",
                   "USAGE"           : "IP Range for Floating IP's",
                   "PROMPT"          : "Enter the IP Range for Floating IP's",
                   "OPTION_LIST"     : ["^([\d]{1,3}\.){3}[\d]{1,3}/\d\d?$"],
                   "VALIDATION_FUNC" : validate.validateRe,
                   "DEFAULT_VALUE"   : "10.3.4.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FLOATRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Scheduler service",
                   "PROMPT"          : "Enter the IP address of the Nova Scheduler service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateSSH,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "PROCESSOR_ARGS"  : {"allow_localhost": True},
                   "PROCESSOR_FUNC"  : process.processHost,
                   "PROCESSOR_MSG"   : "WARN_VAL_IS_HOSTNAME",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "NOVA",
                  "DESCRIPTION"           : "Nova Options",
                  "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return

    novaapisteps = [
             {'title': 'Adding Nova API Manifest entries', 'functions':[createapimanifest]},
             {'title': 'Adding Nova Keystone Manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Nova Cert Manifest entries', 'functions':[createcertmanifest]},
             {'title': 'Adding Nova Compute Manifest entries', 'functions':[createcomputemanifest]},
             {'title': 'Adding Nova Network Manifest entries', 'functions':[createnetworkmanifest]},
             {'title': 'Adding Nova Scheduler Manifest entries', 'functions':[createschedmanifest]},
             {'title': 'Adding Nova VNC Proxy Manifest entries', 'functions':[createvncproxymanifest]},
             {'title': 'Adding Nova Common Manifest entries', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing Nova API", [], [], novaapisteps)

def createapimanifest():
    manifestfile = "%s_api_nova.pp"%controller.CONF['CONFIG_NOVA_API_HOST']
    manifestdata = getManifestTemplate("nova_api.pp")
    appendManifestFile(manifestfile, manifestdata, 'novaapi')

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_nova.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcertmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_CERT_HOST']
    manifestdata = getManifestTemplate("nova_cert.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcomputemanifest():
    for host in controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(","):
        controller.CONF["CONFIG_NOVA_COMPUTE_HOST"] = host
        manifestdata = getManifestTemplate("nova_compute.pp")
        manifestfile = "%s_nova.pp"%host

        server = utils.ScriptRunner(host)
        nova_config_options = NovaConfig()

        if host != controller.CONF["CONFIG_NOVA_NETWORK_HOST"]:
            nova_config_options.addOption("flat_interface", controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
            validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])

        server.execute()
        appendManifestFile(manifestfile, manifestdata + "\n" + nova_config_options.getManifestEntry())

def createnetworkmanifest():
    hostname = controller.CONF['CONFIG_NOVA_NETWORK_HOST']

    server = utils.ScriptRunner(hostname)
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_NETWORK_PRIVIF'])
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_NETWORK_PUBIF'])
    server.execute()

    manifestfile = "%s_nova.pp"%hostname
    manifestdata = getManifestTemplate("nova_network.pp")
    appendManifestFile(manifestfile, manifestdata)

def createschedmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_SCHED_HOST']
    manifestdata = getManifestTemplate("nova_sched.pp")
    appendManifestFile(manifestfile, manifestdata)

def createvncproxymanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_VNCPROXY_HOST']
    manifestdata = getManifestTemplate("nova_vncproxy.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)

