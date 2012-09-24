"""
Installs and configures nova
"""

import logging
import os

import engine_validators as validate
import common_utils as utils
from ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "novaapi-host",
                   "USAGE"           : "Hostname of the Nova API server",
                   "PROMPT"          : "Hostname of the Nova API server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_API_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacert-host",
                   "USAGE"           : "Hostname of the Nova CERT server",
                   "PROMPT"          : "Hostname of the Nova CERT server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_CERT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-hosts",
                   "USAGE"           : "Hostname of the Nova Compute servers (commma seperated)",
                   "PROMPT"          : "Hostname of the Nova Compute server (commma seperated)",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateMultiPing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_HOSTS",
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
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-host",
                   "USAGE"           : "Hostname of the Nova Network server",
                   "PROMPT"          : "Hostname of the Nova Network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-pubif",
                   "USAGE"           : "Public interface on the Nova network server",
                   "PROMPT"          : "Public interface on the Nova network server",
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
                   "PROMPT"          : "Private interface for Flat DHCP on the Nova network server",
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
                   "USAGE"           : "Fixed IP Range for Flat DHCP",
                   "PROMPT"          : "Fixed IP Range for Flat DHCP",
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
                   "USAGE"           : "Fixed IP Range for Floating IP's",
                   "PROMPT"          : "Fixed IP Range for Floating  IP's",
                   "OPTION_LIST"     : ["^([\d]{1,3}\.){3}[\d]{1,3}/\d\d?$"],
                   "VALIDATION_FUNC" : validate.validateRe,
                   "DEFAULT_VALUE"   : "10.3.4.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FLOATINGRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "Hostname of the Nova Sched server",
                   "PROMPT"          : "Hostname of the Nova Sched server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novavolume-host",
                   "USAGE"           : "Hostname of the Nova Volume server",
                   "PROMPT"          : "Hostname of the Nova Volume server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_VOLUME_HOST",
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
             {'title': 'Adding Nova Volume Manifest entries', 'functions':[createvolumemanifest]},
             {'title': 'Adding Nova Common Manifest entries', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing Nova API", [], [], novaapisteps)

def createapimanifest():
    manifestfile = "%s_api_nova.pp"%controller.CONF['CONFIG_NOVA_API_HOST']
    manifestdata = getManifestTemplate("nova_api.pp")
    appendManifestFile(manifestfile, manifestdata)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_nova.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcertmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_CERT_HOST']
    manifestdata = getManifestTemplate("nova_cert.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcomputemanifest():
    manifestdata = getManifestTemplate("nova_compute.pp")
    for host in controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(","):
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

def createvolumemanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_VOLUME_HOST']
    manifestdata = getManifestTemplate("nova_volume.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile in controller.CONF['CONFIG_MANIFESTFILES']:
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)

