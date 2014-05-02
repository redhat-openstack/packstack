"""
Installs and configures nova
"""

import os
import uuid
import logging
import platform
import socket

from packstack.installer import basedefs, processors, utils, validators
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile, manifestfiles

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    if platform.linux_distribution()[0] == "Fedora":
        primary_netif = "em1"
        secondary_netif = "em2"
    else:
        primary_netif = "eth0"
        secondary_netif = "eth1"

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
                   "DEFAULT_VALUE"   : secondary_netif,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-hosts",
                   "USAGE"           : "The list of IP addresses of the server on which to install the Nova Network service",
                   "PROMPT"          : "Enter list of IP addresses on which to install the Nova Network service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_multi_ip, validators.validate_multi_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-manager",
                   "USAGE"           : "Nova network manager",
                   "PROMPT"          : "Enter the Nova network manager",
                   "OPTION_LIST"     : [r'^nova\.network\.manager\.\w+Manager$'],
                   "VALIDATORS"      : [validators.validate_regexp],
                   "DEFAULT_VALUE"   : "nova.network.manager.FlatDHCPManager",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_MANAGER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-pubif",
                   "USAGE"           : "Public interface on the Nova network server",
                   "PROMPT"          : "Enter the Public interface on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : primary_netif,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PUBIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-privif",
                   "USAGE"           : "Private interface for network manager on the Nova network server",
                   "PROMPT"          : "Enter the Private interface for network manager on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : secondary_netif,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-fixed-range",
                   "USAGE"           : "IP Range for network manager",
                   "PROMPT"          : "Enter the IP Range for network manager",
                   "OPTION_LIST"     : ["^[\:\.\da-fA-f]+(\/\d+){0,1}$"],
                   "PROCESSORS"      : [processors.process_cidr],
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
                   "OPTION_LIST"     : ["^[\:\.\da-fA-f]+(\/\d+){0,1}$"],
                   "PROCESSORS"      : [processors.process_cidr],
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
             "NOVA_NETWORK_VLAN" : [
                  {"CMD_OPTION"      : "novanetwork-vlan-start",
                   "USAGE"           : "First VLAN for private networks",
                   "PROMPT"          : "Enter first VLAN for private networks",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : 100,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_VLAN_START",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-num-networks",
                   "USAGE"           : "Number of networks to support",
                   "PROMPT"          : "How many networks should be supported",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : 1,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_NUMBER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-network-size",
                   "USAGE"           : "Number of addresses in each private subnet",
                   "PROMPT"          : "How many addresses should be in each private subnet",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : 255,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_SIZE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ],
             "NOVA_VCENTER": [
                  {"CMD_OPTION"      : "nova-vcenter-host",
                   "USAGE"           : ("The IP address of the VMware vCenter server"),
                   "PROMPT"          : ("Enter the IP address of the VMware vCenter server to use with Nova"),
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ip],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nova-vcenter-username",
                   "USAGE"           : ("The username to authenticate to VMware vCenter server"),
                   "PROMPT"          : ("Enter the username to authenticate on VMware vCenter server"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  {"CMD_OPTION"      : "nova-vcenter-password",
                   "USAGE"           : ("The password to authenticate to VMware vCenter server"),
                   "PROMPT"          : ("Enter the password to authenticate on VMware vCenter server"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_PASSWORD",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  {"CMD_OPTION"      : "nova-vcenter-cluster",
                   "USAGE"           : ("The name of the vCenter cluster"),
                   "PROMPT"          : ("Enter the name of the vCenter datastore"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_CLUSTER_NAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},                   
                  ],
              }

    def use_nova_network(config):
        return config['CONFIG_NOVA_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_INSTALL'] != 'y'

    def use_nova_network_vlan(config):
        manager = 'nova.network.manager.VlanManager'
        return config['CONFIG_NOVA_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_INSTALL'] != 'y' and \
               config['CONFIG_NOVA_NETWORK_MANAGER'] == manager

    def use_nova_vcenter(config):
        return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_VMWARE_BACKEND'] == 'y')

    nova_groups = [
         {"GROUP_NAME"            : "NOVA",
          "DESCRIPTION"           : "Nova Options",
          "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
          "PRE_CONDITION_MATCH"   : "y",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True},
         {"GROUP_NAME"            : "NOVA_NETWORK",
          "DESCRIPTION"           : "Nova Network Options",
          "PRE_CONDITION"         : use_nova_network,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True},
         {"GROUP_NAME"            : "NOVA_NETWORK_VLAN",
          "DESCRIPTION"           : "Nova Network VLAN Options",
          "PRE_CONDITION"         : use_nova_network_vlan,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True},
         {"GROUP_NAME"            : "NOVA_VCENTER",
          "DESCRIPTION"           : "Nova VMware vCenter Config parameters",
          "PRE_CONDITION"         : use_nova_vcenter,
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
             {'title': 'Creating ssh keys for Nova migration',
              'functions':[create_ssh_keys]},
             {'title': 'Gathering ssh host keys for Nova migration',
              'functions':[gather_host_keys]},
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
    # Since this step is running first, let's create necesary variables here
    # and make them global
    global compute_hosts, network_hosts
    com_var = config.get("CONFIG_NOVA_COMPUTE_HOSTS", "")
    compute_hosts = set([i.strip() for i in com_var.split(",") if i.strip()])
    net_var = config.get("CONFIG_NOVA_NETWORK_HOSTS", "")
    network_hosts = set([i.strip() for i in net_var.split(",") if i.strip()])

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


def create_ssh_keys(config):
    migration_key = os.path.join(basedefs.VAR_DIR, 'nova_migration_key')
    # Generate key
    local = utils.ScriptRunner()
    local.append('ssh-keygen -t rsa -b 2048 -f "%s" -N ""' % migration_key)
    local.execute()

    with open(migration_key) as fp:
        secret = fp.read().strip()
    with open('%s.pub' % migration_key) as fp:
        public = fp.read().strip()

    config['NOVA_MIGRATION_KEY_TYPE'] = 'ssh-rsa'
    config['NOVA_MIGRATION_KEY_PUBLIC'] = public.split()[1]
    config['NOVA_MIGRATION_KEY_SECRET'] = secret

def gather_host_keys(config):
    global compute_hosts

    for host in compute_hosts:
        local = utils.ScriptRunner()
        local.append('ssh-keyscan %s' % host)
        retcode, hostkey = local.execute()
        config['HOST_KEYS_%s' % host] = hostkey

def createcomputemanifest(config):
    global compute_hosts, network_hosts

    ssh_hostkeys = ''
    for host in compute_hosts:
        try:
            host_name, host_aliases, host_addrs = socket.gethostbyaddr(host)
        except socket.herror:
            host_name, host_aliases, host_addrs = (host, [], [])

        for hostkey in config['HOST_KEYS_%s' %host].split('\n'):
            hostkey = hostkey.strip()
            if not hostkey:
                continue

            _, host_key_type, host_key_data = hostkey.split()
            config['SSH_HOST_NAME'] = host_name
            config['SSH_HOST_ALIASES'] = ','.join('"%s"' % addr
                   for addr in host_aliases + host_addrs)
            config['SSH_HOST_KEY'] = host_key_data
            config['SSH_HOST_KEY_TYPE'] = host_key_type
            ssh_hostkeys += getManifestTemplate("sshkey.pp")

    for host in compute_hosts:
        config["CONFIG_NOVA_COMPUTE_HOST"] = host
        manifestdata = getManifestTemplate("nova_compute.pp")
        if config['CONFIG_VMWARE_BACKEND'] == 'y':
            manifestdata += getManifestTemplate("nova_compute_vmware.pp")
        else:
            manifestdata += getManifestTemplate("nova_compute_libvirt.pp")
        if (config['CONFIG_VMWARE_BACKEND'] != 'y' and
            config['CONFIG_CINDER_INSTALL'] == 'y' and 
            config['CONFIG_CINDER_BACKEND'] == 'gluster'):
            manifestdata += getManifestTemplate("nova_gluster.pp")
        if (config['CONFIG_VMWARE_BACKEND'] != 'y' and
            config['CONFIG_CINDER_INSTALL'] == 'y' and
            config['CONFIG_CINDER_BACKEND'] == 'nfs'):
            manifestdata += getManifestTemplate("nova_nfs.pp")
        manifestfile = "%s_nova.pp" % host

        nova_config_options = NovaConfig()
        if config['CONFIG_NEUTRON_INSTALL'] != 'y':
            if host not in network_hosts:
                nova_config_options.addOption("DEFAULT/flat_interface",
                                        config['CONFIG_NOVA_COMPUTE_PRIVIF'])
            check_ifcfg(host, config['CONFIG_NOVA_COMPUTE_PRIVIF'])
            try:
                bring_up_ifcfg(host, config['CONFIG_NOVA_COMPUTE_PRIVIF'])
            except ScriptRuntimeError as ex:
                # just warn user to do it by himself
                controller.MESSAGES.append(str(ex))

        if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
            manifestdata += getManifestTemplate(get_mq(config, "nova_ceilometer"))

        # According to the docs the only element that connects directly to nova compute
        # is nova scheduler
        # http://docs.openstack.org/developer/nova/nova.concepts.html#concept-system-architecture
        config['FIREWALL_ALLOWED'] = "'%s'" % (config['CONFIG_NOVA_SCHED_HOST'].strip())
        config['FIREWALL_SERVICE_NAME'] = "nova compute"
        config['FIREWALL_SERVICE_ID'] = "nova_compute"
        config['FIREWALL_PORTS'] = "'5900-5999'"
        config['FIREWALL_CHAIN'] = "INPUT"
        manifestdata += getManifestTemplate("firewall.pp")

        manifestdata += "\n" + nova_config_options.getManifestEntry()
        manifestdata += "\n" + ssh_hostkeys
        appendManifestFile(manifestfile, manifestdata)


def createnetworkmanifest(config):
    global compute_hosts, network_hosts
    if config['CONFIG_NEUTRON_INSTALL'] == "y":
        return

    # set default values for VlanManager in case this values are not in config
    for key, value in [('CONFIG_NOVA_NETWORK_VLAN_START', 100),
                       ('CONFIG_NOVA_NETWORK_SIZE', 255),
                       ('CONFIG_NOVA_NETWORK_NUMBER', 1)]:
        config[key] = config.get(key, value)

    api_host = config['CONFIG_NOVA_API_HOST']
    multihost = len(network_hosts) > 1
    config['CONFIG_NOVA_NETWORK_MULTIHOST'] = multihost and 'true' or 'false'
    for host in network_hosts:
        for i in ('CONFIG_NOVA_NETWORK_PRIVIF', 'CONFIG_NOVA_NETWORK_PUBIF'):
            check_ifcfg(host, config[i])
            try:
                bring_up_ifcfg(host, config[i])
            except ScriptRuntimeError as ex:
                # just warn user to do it by himself
                controller.MESSAGES.append(str(ex))

        key = 'CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'
        config[key] = config[key] == "y"

        # We need to explicitly set the network size
        routing_prefix = config['CONFIG_NOVA_NETWORK_FIXEDRANGE'].split('/')[1]
        net_size = 2**(32 - int(routing_prefix))
        config['CONFIG_NOVA_NETWORK_FIXEDSIZE'] = str(net_size)

        manifestfile = "%s_nova.pp" % host
        manifestdata = getManifestTemplate("nova_network.pp")

        # in multihost mode each compute host runs nova-api-metadata
        if multihost and host != api_host and host in compute_hosts:
            manifestdata += getManifestTemplate("nova_metadata.pp")
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
    global compute_hosts, network_hosts
    network_type = (config['CONFIG_NEUTRON_INSTALL'] == "y" and
                    'neutron' or 'nova')
    network_multi = len(network_hosts) > 1
    dirty = [config.get('CONFIG_NOVA_CONDUCTOR_HOST'),
             config.get('CONFIG_NOVA_API_HOST'),
             config.get('CONFIG_NOVA_CERT_HOST'),
             config.get('CONFIG_NOVA_VNCPROXY_HOST'),
             config.get('CONFIG_NOVA_SCHED_HOST')]
    dbacces_hosts = set([i.strip() for i in dirty if i and i.strip()])
    dbacces_hosts |= network_hosts

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            host, manifest = manifestfile.split('_', 1)
            host = host.strip()

            if host in compute_hosts and host not in dbacces_hosts:
                # we should omit password in case we are installing only
                # nova-compute to the host
                perms = "nova"
            else:
                perms = "nova:%(CONFIG_NOVA_DB_PW)s"
            sqlconn = "mysql://%s@%%(CONFIG_MYSQL_HOST)s/nova" % perms
            config['CONFIG_NOVA_SQL_CONN'] = sqlconn % config

            # for nova-network in multihost mode each compute host is metadata
            # host otherwise we use api host
            if (network_type == 'nova' and network_multi and
                host in compute_hosts):
                metadata = host
            else:
                metadata = config['CONFIG_NOVA_API_HOST']
            config['CONFIG_NOVA_METADATA_HOST'] = metadata

            data = getManifestTemplate(get_mq(config, "nova_common"))
            data += getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)


def createneutronmanifest(config):
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] != "y":
        return

    controller.CONF['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_neutron.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
