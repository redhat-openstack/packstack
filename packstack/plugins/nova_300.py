"""
Installs and configures nova
"""

import os
import uuid
import logging

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
import packstack.installer.common_utils as utils
from packstack.installer.exceptions import ScriptRuntimeError

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
                   "VALIDATORS"      : [validate.validate_ip, validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
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
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
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
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
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
                   "VALIDATORS"      : [validate.validate_multi_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova compute servers",
                   "PROMPT"          : "Enter the Private interface for Flat DHCP on the Nova compute servers",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : utils.getNics(),
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
                   "VALIDATORS"      : [validate.validate_ip, validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nova-db-passwd",
                   "USAGE"           : "The password to use for the Nova to access DB",
                   "PROMPT"          : "Enter the password for the Nova DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nova-ks-passwd",
                   "USAGE"           : "The password to use for the Nova to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Nova Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-pubif",
                   "USAGE"           : "Public interface on the Nova network server",
                   "PROMPT"          : "Enter the Public interface on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : utils.getNics(),
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
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : utils.getNics(),
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
                   "VALIDATORS"      : [validate.validate_regexp],
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
                   "VALIDATORS"      : [validate.validate_regexp],
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
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-cpu-allocation-ratio",
                   "USAGE"           : "The overcommitment ratio for virtual to physical CPUs. "
                                       "Set to 1.0 to disable CPU overcommitment",
                   "PROMPT"          : "Enter the CPU overcommitment ratio. "
                                       "Set to 1.0 to disable CPU overcommitment",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_float],
                   "DEFAULT_VALUE"   : 16.0,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-ram-allocation-ratio",
                   "USAGE"           : "The overcommitment ratio for virtual to physical RAM. "
                                       "Set to 1.0 to disable RAM overcommitment",
                   "PROMPT"          : "Enter the RAM overcommitment ratio. "
                                       "Set to 1.0 to disable RAM overcommitment",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_float],
                   "DEFAULT_VALUE"   : 1.5,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO",
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
             {'title': 'Adding Nova API manifest entries', 'functions':[createapimanifest]},
             {'title': 'Adding Nova Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Nova Cert manifest entries', 'functions':[createcertmanifest]},
             {'title': 'Adding Nova Compute manifest entries', 'functions':[createcomputemanifest]},
             {'title': 'Adding Nova Network manifest entries', 'functions':[createnetworkmanifest]},
             {'title': 'Adding Nova Scheduler manifest entries', 'functions':[createschedmanifest]},
             {'title': 'Adding Nova VNC Proxy manifest entries', 'functions':[createvncproxymanifest]},
             {'title': 'Adding Nova Common manifest entries', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing OpenStack Nova API", [], [], novaapisteps)


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


def check_ifcfg(host, device):
    """
    Raises ScriptRuntimeError if given host does not have give device.
    """
    server = utils.ScriptRunner(host)
    cmd = "ip addr show dev %s || ( echo Device %s does not exist && exit 1 )"
    server.append(cmd % (device, device))
    server.execute()


def bring_up_ifcfg(host, device):
    """
    Brings given device up if it's down. Raises ScriptRuntimeError in case
    of failure.
    """
    server = utils.ScriptRunner(host)
    server.append('ip link show up | grep "%s"' % device)
    try:
        server.execute()
    except ScriptRuntimeError:
        server.clear()
        cmd = 'ip link set dev %s up'
        server.append(cmd % device)
        try:
            server.execute()
        except ScriptRuntimeError:
            msg = ('Failed to bring up network interface %s on host %s.'
                   ' Interface should be up so Openstack can work'
                   ' properly.' % (device, host))
            raise ScriptRuntimeError(msg)


def createcomputemanifest():
    for host in controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(","):
        controller.CONF["CONFIG_NOVA_COMPUTE_HOST"] = host
        manifestdata = getManifestTemplate("nova_compute.pp")
        manifestfile = "%s_nova.pp"%host

        nova_config_options = NovaConfig()
        if host != controller.CONF["CONFIG_NOVA_NETWORK_HOST"]:
            nova_config_options.addOption("DEFAULT/flat_interface", controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
        check_ifcfg(host, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
        try:
            bring_up_ifcfg(host, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
        except ScriptRuntimeError, ex:
            # just warn user to do it by himself
            controller.MESSAGES.append(str(ScriptRuntimeError))

        appendManifestFile(manifestfile, manifestdata + "\n" + nova_config_options.getManifestEntry())


def createnetworkmanifest():
    host = controller.CONF['CONFIG_NOVA_NETWORK_HOST']
    for i in ('CONFIG_NOVA_NETWORK_PRIVIF', 'CONFIG_NOVA_NETWORK_PUBIF'):
        check_ifcfg(host, controller.CONF[i])
        try:
            bring_up_ifcfg(host, controller.CONF[i])
        except ScriptRuntimeError, ex:
            # just warn user to do it by himself
            controller.MESSAGES.append(str(ScriptRuntimeError))

    manifestfile = "%s_nova.pp" % host
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
