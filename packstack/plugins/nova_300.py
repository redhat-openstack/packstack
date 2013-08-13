"""
Installs and configures nova
"""

import os
import uuid
import logging

from packstack.installer import validators
from packstack.installer import utils
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules.ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile, manifestfiles

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    nova_params = {
            "NOVA" : [
                  {"CMD_OPTION"      : "novaapi-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova API service",
                   "PROMPT"          : "Enter the IP address of the Nova API service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ip, validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
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
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
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
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
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
                   "VALIDATORS"      : [validators.validate_not_empty, validators.validate_multi_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novaconductor-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Conductor service",
                   "PROMPT"          : "Enter the IP address of the Nova Conductor service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ip, validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_CONDUCTOR_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nova-db-passwd",
                   "USAGE"           : "The password to use for the Nova to access DB",
                   "PROMPT"          : "Enter the password for the Nova DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
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
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Scheduler service",
                   "PROMPT"          : "Enter the IP address of the Nova Scheduler service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
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
                   "VALIDATORS"      : [validators.validate_float],
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
                   "VALIDATORS"      : [validators.validate_float],
                   "DEFAULT_VALUE"   : 1.5,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ],
             "NOVA_NETWORK" : [
                  {"CMD_OPTION"      : "novacompute-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova compute servers",
                   "PROMPT"          : "Enter the Private interface for Flat DHCP on the Nova compute servers",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
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
                   "VALIDATORS"      : [validators.validate_ip, validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
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
                   "VALIDATORS"      : [validators.validate_not_empty],
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
                   "VALIDATORS"      : [validators.validate_not_empty],
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
                   "VALIDATORS"      : [validators.validate_regexp],
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
                   "VALIDATORS"      : [validators.validate_regexp],
                   "DEFAULT_VALUE"   : "10.3.4.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FLOATRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-default-floating-pool",
                   "USAGE"           : "Name of the default floating pool to which the specified floating ranges are added to",
                   "PROMPT"          : "What should the default floating pool be called?",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "nova",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-auto-assign-floating-ip",
                   "USAGE"           : "Automatically assign a floating IP to new instances",
                   "PROMPT"          : "Should new instances automatically have a floating IP assigned?",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ],
              }

    def use_nova_network(config):
        return config['CONFIG_NOVA_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_INSTALL'] != 'y'

    nova_groups = [
        { "GROUP_NAME"            : "NOVA",
          "DESCRIPTION"           : "Nova Options",
          "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
          "PRE_CONDITION_MATCH"   : "y",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True},
        { "GROUP_NAME"            : "NOVA_NETWORK",
          "DESCRIPTION"           : "Nova Network Options",
          "PRE_CONDITION"         : use_nova_network,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True},
        ]

    for group in nova_groups:
        paramList = nova_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)

def initSequences(controller):
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return

    novaapisteps = [
             {'title': 'Adding Nova API manifest entries', 'functions':[createapimanifest]},
             {'title': 'Adding Nova Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Nova Cert manifest entries', 'functions':[createcertmanifest]},
             {'title': 'Adding Nova Conductor manifest entries', 'functions':[createconductormanifest]},
             {'title': 'Adding Nova Compute manifest entries', 'functions':[createcomputemanifest]},
             {'title': 'Adding Nova Scheduler manifest entries', 'functions':[createschedmanifest]},
             {'title': 'Adding Nova VNC Proxy manifest entries', 'functions':[createvncproxymanifest]},
             {'title': 'Adding Nova Common manifest entries', 'functions':[createcommonmanifest]},
    ]

    if controller.CONF['CONFIG_NEUTRON_INSTALL'] == 'y':
        novaapisteps.append({'title': 'Adding Openstack Network-related Nova manifest entries', 'functions':[createneutronmanifest]})
    else:
        novaapisteps.append({'title': 'Adding Nova Network manifest entries', 'functions':[createnetworkmanifest]})

    controller.addSequence("Installing OpenStack Nova API", [], [], novaapisteps)


def createapimanifest(config):
    # This is a hack around us needing to generate the neutron metadata
    # password, but the nova puppet plugin uses the existence of that
    # password to determine whether or not to configure neutron metadata
    # proxy support. So the nova_api.pp template needs unquoted 'undef'
    # to disable metadata support if neutron is not being installed.
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] != 'y':
        controller.CONF['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = 'undef'
    else:
        controller.CONF['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = \
            "'%s'" % controller.CONF['CONFIG_NEUTRON_METADATA_PW']
    manifestfile = "%s_api_nova.pp"%controller.CONF['CONFIG_NOVA_API_HOST']
    manifestdata = getManifestTemplate("nova_api.pp")
    appendManifestFile(manifestfile, manifestdata, 'novaapi')


def createkeystonemanifest(config):
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_nova.pp")
    appendManifestFile(manifestfile, manifestdata)


def createcertmanifest(config):
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_CERT_HOST']
    manifestdata = getManifestTemplate("nova_cert.pp")
    appendManifestFile(manifestfile, manifestdata)


def createconductormanifest(config):
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_CONDUCTOR_HOST']
    manifestdata = getManifestTemplate("nova_conductor.pp")
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


def createcomputemanifest(config):
    dirty = controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(",")
    hostlist = [i.strip() for i in dirty if i.strip()]
    for host in hostlist:
        controller.CONF["CONFIG_NOVA_COMPUTE_HOST"] = host
        manifestdata = getManifestTemplate("nova_compute.pp")
        if controller.CONF['CONFIG_CINDER_INSTALL'] == 'y' and controller.CONF['CONFIG_CINDER_BACKEND'] == 'gluster':
            manifestdata += getManifestTemplate("nova_gluster.pp")
        if controller.CONF['CONFIG_CINDER_INSTALL'] == 'y' and controller.CONF['CONFIG_CINDER_BACKEND'] == 'nfs':
            manifestdata += getManifestTemplate("nova_nfs.pp")
        manifestfile = "%s_nova.pp"%host

        nova_config_options = NovaConfig()
        if controller.CONF['CONFIG_NEUTRON_INSTALL'] != 'y':
            if host != controller.CONF["CONFIG_NOVA_NETWORK_HOST"]:
                nova_config_options.addOption("DEFAULT/flat_interface", controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
            check_ifcfg(host, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
            try:
                bring_up_ifcfg(host, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
            except ScriptRuntimeError, ex:
                # just warn user to do it by himself
                controller.MESSAGES.append(str(ScriptRuntimeError))

        appendManifestFile(manifestfile, manifestdata + "\n" + nova_config_options.getManifestEntry())


def createnetworkmanifest(config):
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] == "y":
        return

    host = controller.CONF['CONFIG_NOVA_NETWORK_HOST']
    for i in ('CONFIG_NOVA_NETWORK_PRIVIF', 'CONFIG_NOVA_NETWORK_PUBIF'):
        check_ifcfg(host, controller.CONF[i])
        try:
            bring_up_ifcfg(host, controller.CONF[i])
        except ScriptRuntimeError, ex:
            # just warn user to do it by himself
            controller.MESSAGES.append(str(ScriptRuntimeError))

    if controller.CONF['CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'] == "y":
      controller.CONF['CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'] = True
    else:
      controller.CONF['CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'] = False

    # We need to explicitly set the network size
    routing_prefix = controller.CONF['CONFIG_NOVA_NETWORK_FIXEDRANGE'].split('/')[1]
    net_size = 2**(32 - int(routing_prefix))
    controller.CONF['CONFIG_NOVA_NETWORK_FIXEDSIZE'] = str(net_size)

    manifestfile = "%s_nova.pp" % host
    manifestdata = getManifestTemplate("nova_network.pp")
    appendManifestFile(manifestfile, manifestdata)


def createschedmanifest(config):
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_SCHED_HOST']
    manifestdata = getManifestTemplate("nova_sched.pp")
    appendManifestFile(manifestfile, manifestdata)


def createvncproxymanifest(config):
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_VNCPROXY_HOST']
    manifestdata = getManifestTemplate("nova_vncproxy.pp")
    appendManifestFile(manifestfile, manifestdata)


def createcommonmanifest(config):
    dbhost = config['CONFIG_MYSQL_HOST']
    dirty = controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(",")
    nopass_nodes = [i.strip() for i in dirty if i.strip()]
    dirty = [config.get('CONFIG_NOVA_CONDUCTOR_HOST'),
             config.get('CONFIG_NOVA_API_HOST'),
             config.get('CONFIG_NOVA_CERT_HOST'),
             config.get('CONFIG_NOVA_VNCPROXY_HOST'),
             config.get('CONFIG_NOVA_SCHED_HOST'),
             config.get('CONFIG_NOVA_NETWORK_HOST')]
    dbpass_nodes = [i.strip() for i in dirty if i and i.strip()]

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            host, manifest = manifestfile.split('_', 1)
            host = host.strip()

            if host in nopass_nodes and host not in dbpass_nodes:
                # we should omit password in case we are installing only
                # nova-compute to the host
                perms = "nova"
            else:
                perms = "nova:%(CONFIG_NOVA_DB_PW)s" % config
            config['CONFIG_NOVA_SQL_CONN'] = ("mysql://%s@%s/nova"
                                              % (perms, dbhost))

            data = getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)


def createneutronmanifest(config):
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] != "y":
        return

    if controller.CONF['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch':
        controller.CONF['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = 'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver'
    else:
        controller.CONF['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_neutron.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
