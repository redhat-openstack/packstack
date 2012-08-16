"""
Installs and configures nova
"""

import logging
import os

import engine_validators as validate
import common_utils as utils
import ospluginutils

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"
PUPPET_DIR = "puppet"
PUPPET_MANIFEST_DIR = os.path.join(PUPPET_DIR, "manifests")
PUPPET_TEMPLATE_DIR = os.path.join(PUPPET_DIR, "templates")

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
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVAAPI_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacert-host",
                   "USAGE"           : "Hostname of the Nova CERT server",
                   "PROMPT"          : "Hostname of the Nova CERT server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVACERT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
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
                  {"CMD_OPTION"      : "novanetwork-host",
                   "USAGE"           : "Hostname of the Nova Network server",
                   "PROMPT"          : "Hostname of the Nova Network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVANETWORK_HOST",
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
                   "CONF_NAME"       : "CONFIG_NOVANETWORK_PRIVIF",
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
                   "CONF_NAME"       : "CONFIG_NOVANETWORK_PUBIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "Hostname of the Nova Sched server",
                   "PROMPT"          : "Hostname of the Nova Sched server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVASCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novavolume-host",
                   "USAGE"           : "Hostname of the Nova Volume server",
                   "PROMPT"          : "Hostname of the Nova Volume server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "localhost",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVAVOLUME_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "NOVA",
                  "DESCRIPTION"           : "Nova Options",
                  "PRE_CONDITION"         : "CONFIG_OS_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    if controller.CONF['CONFIG_OS_NOVA_INSTALL'] != 'y':
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

def getManifestTemplate(template_name):
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read()%controller.CONF

def appendManifestFile(manifest_name, data):
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, manifest_name)
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)
    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(data)
    
def createapimanifest():
    manifestfile = "%s_api_nova.pp"%controller.CONF['CONFIG_NOVAAPI_HOST']
    manifestdata = getManifestTemplate("nova_api.pp")
    appendManifestFile(manifestfile, manifestdata)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_nova.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcertmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVACERT_HOST']
    manifestdata = getManifestTemplate("nova_cert.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcomputemanifest():
    manifestdata = getManifestTemplate("nova_compute.pp")
    for host in controller.CONF["CONFIG_NOVACOMPUTE_HOSTS"].split(","):
        manifestfile = "%s_nova.pp"%host

        server = utils.ScriptRunner(host)
        nova_config_options = ospluginutils.NovaConfig()

        if host != controller.CONF["CONFIG_NOVANETWORK_HOST"]:
            nova_config_options.addOption("flat_interface", controller.CONF['CONFIG_NOVACOMPUTE_PRIVIF'])
            validate.r_validateIF(server, controller.CONF['CONFIG_NOVACOMPUTE_PRIVIF'])

        server.execute()
        appendManifestFile(manifestfile, manifestdata + "\n" + nova_config_options.getManifestEntry())

def createnetworkmanifest():
    hostname = controller.CONF['CONFIG_NOVANETWORK_HOST']

    server = utils.ScriptRunner(hostname)
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVANETWORK_PRIVIF'])
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVANETWORK_PUBIF'])
    server.execute()

    manifestfile = "%s_nova.pp"%hostname
    manifestdata = getManifestTemplate("nova_network.pp")
    appendManifestFile(manifestfile, manifestdata)

def createschedmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVASCHED_HOST']
    manifestdata = getManifestTemplate("nova_sched.pp")
    appendManifestFile(manifestfile, manifestdata)

def createvolumemanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVAVOLUME_HOST']
    manifestdata = getManifestTemplate("nova_volume.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile in controller.CONF['CONFIG_MANIFESTFILES']:
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)

