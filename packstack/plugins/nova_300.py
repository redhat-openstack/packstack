# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Installs and configures Nova
"""

import os
import platform
import socket

from packstack.installer import basedefs
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules import common
from packstack.modules.documentation import update_params_usage
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import deliver_ssl_file
from packstack.modules.ospluginutils import getManifestTemplate
from packstack.modules.ospluginutils import generate_ssl_cert
from packstack.modules.ospluginutils import manifestfiles

# ------------- Nova Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Nova"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    if platform.linux_distribution()[0] == "Fedora":
        primary_netif = "em1"
        secondary_netif = "em2"
    else:
        primary_netif = "eth0"
        secondary_netif = "eth1"

    nova_params = {
        "NOVA": [
            {"CMD_OPTION": "nova-db-passwd",
             "PROMPT": "Enter the password for the Nova DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ks-passwd",
             "PROMPT": "Enter the password for the Nova Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "novasched-cpu-allocation-ratio",
             "PROMPT": "Enter the CPU overcommitment ratio. Set to 1.0 to "
                       "disable CPU overcommitment",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_float],
             "DEFAULT_VALUE": 16.0,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novasched-ram-allocation-ratio",
             "PROMPT": ("Enter the RAM overcommitment ratio. Set to 1.0 to "
                        "disable RAM overcommitment"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_float],
             "DEFAULT_VALUE": 1.5,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novacompute-migrate-protocol",
             "PROMPT": ("Enter protocol which will be used for instance "
                        "migration"),
             "OPTION_LIST": ['tcp', 'ssh'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'tcp',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-compute-manager",
             "PROMPT": ("Enter the compute manager for nova "
                        "migration"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "nova.compute.manager.ComputeManager",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_COMPUTE_MANAGER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ssl-cert",
             "PROMPT": ("Enter the path to a PEM encoded certificate to be used "
                        "on the https server, leave blank if one should be "
                        "generated, this certificate should not require "
                        "a passphrase"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VNC_SSL_CERT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ssl-key",
             "PROMPT": ("Enter the SSL keyfile corresponding to the certificate "
                        "if one was entered"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VNC_SSL_KEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NOVA_NETWORK": [
            {"CMD_OPTION": "novacompute-privif",
             "PROMPT": ("Enter the Private interface for Flat DHCP on the Nova"
                        " compute servers"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": secondary_netif,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_COMPUTE_PRIVIF",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-manager",
             "PROMPT": "Enter the Nova network manager",
             "OPTION_LIST": [r'^nova\.network\.manager\.\w+Manager$'],
             "VALIDATORS": [validators.validate_regexp],
             "DEFAULT_VALUE": "nova.network.manager.FlatDHCPManager",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_MANAGER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-pubif",
             "PROMPT": "Enter the Public interface on the Nova network server",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": primary_netif,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_PUBIF",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-privif",
             "PROMPT": ("Enter the Private interface for network manager on "
                        "the Nova network server"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": secondary_netif,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_PRIVIF",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-fixed-range",
             "PROMPT": "Enter the IP Range for network manager",
             "OPTION_LIST": ["^[\:\.\da-fA-f]+(\/\d+){0,1}$"],
             "PROCESSORS": [processors.process_cidr],
             "VALIDATORS": [validators.validate_regexp],
             "DEFAULT_VALUE": "192.168.32.0/22",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_FIXEDRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-floating-range",
             "PROMPT": "Enter the IP Range for Floating IP's",
             "OPTION_LIST": ["^[\:\.\da-fA-f]+(\/\d+){0,1}$"],
             "PROCESSORS": [processors.process_cidr],
             "VALIDATORS": [validators.validate_regexp],
             "DEFAULT_VALUE": "10.3.4.0/22",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_FLOATRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-auto-assign-floating-ip",
             "PROMPT": ("Should new instances automatically have a floating "
                        "IP assigned?"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NOVA_NETWORK_VLAN": [
            {"CMD_OPTION": "novanetwork-vlan-start",
             "PROMPT": "Enter first VLAN for private networks",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 100,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_VLAN_START",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-num-networks",
             "PROMPT": "How many networks should be supported",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 1,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_NUMBER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novanetwork-network-size",
             "PROMPT": "How many addresses should be in each private subnet",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 255,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_NETWORK_SIZE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
    }
    update_params_usage(basedefs.PACKSTACK_DOC, nova_params)

    def use_nova_network(config):
        return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_NEUTRON_INSTALL'] != 'y')

    def use_nova_network_vlan(config):
        manager = 'nova.network.manager.VlanManager'
        return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_NEUTRON_INSTALL'] != 'y' and
                config['CONFIG_NOVA_NETWORK_MANAGER'] == manager)

    nova_groups = [
        {"GROUP_NAME": "NOVA",
         "DESCRIPTION": "Nova Options",
         "PRE_CONDITION": "CONFIG_NOVA_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NOVA_NETWORK",
         "DESCRIPTION": "Nova Network Options",
         "PRE_CONDITION": use_nova_network,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NOVA_NETWORK_VLAN",
         "DESCRIPTION": "Nova Network VLAN Options",
         "PRE_CONDITION": use_nova_network_vlan,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in nova_groups:
        params = nova_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return

    if controller.CONF['CONFIG_NEUTRON_INSTALL'] == 'y':
        network_title = ('Adding OpenStack Network-related '
                         'Nova manifest entries')
        network_function = create_neutron_manifest
    else:
        network_title = 'Adding Nova Network manifest entries'
        network_function = create_network_manifest

    novaapisteps = [
        {'title': 'Adding Nova API manifest entries',
         'functions': [create_api_manifest]},
        {'title': 'Adding Nova Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Nova Cert manifest entries',
         'functions': [create_cert_manifest]},
        {'title': 'Adding Nova Conductor manifest entries',
         'functions': [create_conductor_manifest]},
        {'title': 'Creating ssh keys for Nova migration',
         'functions': [create_ssh_keys]},
        {'title': 'Gathering ssh host keys for Nova migration',
         'functions': [gather_host_keys]},
        {'title': 'Adding Nova Compute manifest entries',
         'functions': [create_compute_manifest]},
        {'title': 'Adding Nova Scheduler manifest entries',
         'functions': [create_sched_manifest]},
        {'title': 'Adding Nova VNC Proxy manifest entries',
         'functions': [create_vncproxy_manifest]},
        {'title': network_title,
         'functions': [network_function]},
        {'title': 'Adding Nova Common manifest entries',
         'functions': [create_common_manifest]},
    ]

    controller.addSequence("Installing OpenStack Nova API", [], [],
                           novaapisteps)


# ------------------------- helper functions -------------------------

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
                   ' Interface should be up so OpenStack can work'
                   ' properly.' % (device, host))
            raise ScriptRuntimeError(msg)


# ------------------------ Step Functions -------------------------

def create_ssh_keys(config, messages):
    migration_key = os.path.join(basedefs.VAR_DIR, 'nova_migration_key')
    # Generate key if it does not exist
    if not os.path.exists(migration_key):
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


def gather_host_keys(config, messages):
    global compute_hosts

    for host in compute_hosts:
        local = utils.ScriptRunner()
        local.append('ssh-keyscan %s' % host)
        retcode, hostkey = local.execute()
        config['HOST_KEYS_%s' % host] = hostkey


def create_api_manifest(config, messages):
    # Since this step is running first, let's create necessary variables here
    # and make them global
    global compute_hosts, network_hosts
    com_var = config.get("CONFIG_COMPUTE_HOSTS", "")
    compute_hosts = set([i.strip() for i in com_var.split(",") if i.strip()])
    net_var = config.get("CONFIG_NETWORK_HOSTS", "")
    network_hosts = set([i.strip() for i in net_var.split(",") if i.strip()])

    # This is a hack around us needing to generate the neutron metadata
    # password, but the nova puppet plugin uses the existence of that
    # password to determine whether or not to configure neutron metadata
    # proxy support. So the nova_api.pp template needs to be set to None
    # to disable metadata support if neutron is not being installed.
    if config['CONFIG_NEUTRON_INSTALL'] != 'y':
        config['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = None
    else:
        config['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = "%s" % config['CONFIG_NEUTRON_METADATA_PW']
    manifestfile = "%s_api_nova.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("nova_api")

    fw_details = dict()
    key = "nova_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "nova api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8773', '8774', '8775']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_NOVA_API_RULES'] = fw_details
    manifestdata += createFirewallResources('FIREWALL_NOVA_API_RULES')

    appendManifestFile(manifestfile, manifestdata, 'novaapi')


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_nova")
    appendManifestFile(manifestfile, manifestdata)


def create_cert_manifest(config, messages):
    manifestfile = "%s_nova.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("nova_cert")
    appendManifestFile(manifestfile, manifestdata)


def create_conductor_manifest(config, messages):
    manifestfile = "%s_nova.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("nova_conductor")
    appendManifestFile(manifestfile, manifestdata)


def create_compute_manifest(config, messages):
    global compute_hosts, network_hosts

    if config["CONFIG_HORIZON_SSL"] == 'y':
        config["CONFIG_VNCPROXY_PROTOCOL"] = "https"
    else:
        config["CONFIG_VNCPROXY_PROTOCOL"] = "http"

    migrate_protocol = config['CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL']
    if migrate_protocol == 'ssh':
        config['CONFIG_NOVA_COMPUTE_MIGRATE_URL'] = (
            'qemu+ssh://nova@%s/system?no_verify=1&'
            'keyfile=/etc/nova/ssh/nova_migration_key'
        )
    else:
        config['CONFIG_NOVA_COMPUTE_MIGRATE_URL'] = (
            'qemu+tcp://nova@%s/system'
        )

    ssh_hostkeys = ''

    ssh_keys_details = {}
    for host in compute_hosts:
        try:
            hostname, aliases, addrs = socket.gethostbyaddr(host)
        except socket.herror:
            hostname, aliases, addrs = (host, [], [])

        for hostkey in config['HOST_KEYS_%s' % host].split('\n'):
            hostkey = hostkey.strip()
            if not hostkey:
                continue

            _, host_key_type, host_key_data = hostkey.split()
            key = "%s.%s" % (host_key_type, hostname)
            ssh_keys_details.setdefault(key, {})
            ssh_keys_details[key]['ensure'] = 'present'
            ssh_keys_details[key]['host_aliases'] = aliases + addrs
            ssh_keys_details[key]['key'] = host_key_data
            ssh_keys_details[key]['type'] = host_key_type

    config['SSH_KEYS'] = ssh_keys_details
    ssh_hostkeys += getManifestTemplate("sshkey")

    for host in compute_hosts:
        if config['CONFIG_IRONIC_INSTALL'] == 'y':
            cm = 'ironic.nova.compute.manager.ClusteredComputeManager'
            config['CONFIG_NOVA_COMPUTE_MANAGER'] = cm

        manifestdata = getManifestTemplate("nova_compute")

        fw_details = dict()
        cf_fw_qemu_mig_key = "FIREWALL_NOVA_QEMU_MIG_RULES_%s" % host
        for c_host in compute_hosts:
            key = "nova_qemu_migration_%s_%s" % (host, c_host)
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "%s" % c_host
            fw_details[key]['service_name'] = "nova qemu migration"
            fw_details[key]['chain'] = "INPUT"
            fw_details[key]['ports'] = ['16509', '49152-49215']
            fw_details[key]['proto'] = "tcp"

        config[cf_fw_qemu_mig_key] = fw_details
        manifestdata += createFirewallResources(cf_fw_qemu_mig_key)

        if config['CONFIG_VMWARE_BACKEND'] == 'y':
            manifestdata += getManifestTemplate("nova_compute_vmware.pp")
        elif config['CONFIG_IRONIC_INSTALL'] == 'y':
            manifestdata += getManifestTemplate("nova_compute_ironic.pp")
        else:
            manifestdata += getManifestTemplate("nova_compute_libvirt.pp")

        if (config['CONFIG_VMWARE_BACKEND'] != 'y' and
                config['CONFIG_CINDER_INSTALL'] == 'y' and
                'gluster' in config['CONFIG_CINDER_BACKEND']):
            manifestdata += getManifestTemplate("nova_gluster")
        if (config['CONFIG_VMWARE_BACKEND'] != 'y' and
                config['CONFIG_CINDER_INSTALL'] == 'y' and
                'nfs' in config['CONFIG_CINDER_BACKEND']):
            manifestdata += getManifestTemplate("nova_nfs")
        manifestfile = "%s_nova.pp" % host

        if config['CONFIG_NEUTRON_INSTALL'] != 'y':
            if host not in network_hosts:
                manifestdata += getManifestTemplate('nova_compute_flat')

            if config['CONFIG_USE_SUBNETS'] == 'y':
                netface = common.cidr_to_ifname(
                    config['CONFIG_NOVA_COMPUTE_PRIVIF'], host, config
                )
            else:
                netface = config['CONFIG_NOVA_COMPUTE_PRIVIF']
            check_ifcfg(host, netface)
            try:
                bring_up_ifcfg(host, netface)
            except ScriptRuntimeError as ex:
                # just warn user to do it by himself
                messages.append(str(ex))

        if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
            if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
                ssl_cert_file = config['CONFIG_CEILOMETER_SSL_CERT'] = (
                    '/etc/pki/tls/certs/ssl_amqp_ceilometer.crt'
                )
                ssl_key_file = config['CONFIG_CEILOMETER_SSL_KEY'] = (
                    '/etc/pki/tls/private/ssl_amqp_ceilometer.key'
                )
                ssl_host = config['CONFIG_CONTROLLER_HOST']
                service = 'ceilometer'
                generate_ssl_cert(config, host, service, ssl_key_file,
                                  ssl_cert_file)

            mq_template = get_mq(config, "nova_ceilometer")
            manifestdata += getManifestTemplate(mq_template)
            manifestdata += getManifestTemplate("nova_ceilometer")

        fw_details = dict()
        key = "nova_compute"
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % config['CONFIG_CONTROLLER_HOST']
        fw_details[key]['service_name'] = "nova compute"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['5900-5999']
        fw_details[key]['proto'] = "tcp"
        config['FIREWALL_NOVA_COMPUTE_RULES'] = fw_details

        manifestdata += "\n" + createFirewallResources(
            'FIREWALL_NOVA_COMPUTE_RULES'
            )
        manifestdata += "\n" + ssh_hostkeys
        appendManifestFile(manifestfile, manifestdata)


def create_network_manifest(config, messages):
    global compute_hosts, network_hosts
    if config['CONFIG_NEUTRON_INSTALL'] == "y":
        return

    # set default values for VlanManager in case this values are not in config
    for key, value in [('CONFIG_NOVA_NETWORK_VLAN_START', 100),
                       ('CONFIG_NOVA_NETWORK_SIZE', 255),
                       ('CONFIG_NOVA_NETWORK_NUMBER', 1)]:
        config[key] = config.get(key, value)

    api_host = config['CONFIG_CONTROLLER_HOST']
    multihost = len(network_hosts) > 1
    config['CONFIG_NOVA_NETWORK_MULTIHOST'] = multihost and 'true' or 'false'
    for host in network_hosts:
        for i in ('CONFIG_NOVA_NETWORK_PRIVIF', 'CONFIG_NOVA_NETWORK_PUBIF'):
            netface = config[i]
            if config['CONFIG_USE_SUBNETS'] == 'y':
                netface = common.cidr_to_ifname(netface, host, config)
            check_ifcfg(host, netface)
            try:
                bring_up_ifcfg(host, netface)
            except ScriptRuntimeError as ex:
                # just warn user to do it by himself
                messages.append(str(ex))

        key = 'CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'
        config[key] = config[key] == "y"

        # We need to explicitly set the network size
        routing_prefix = config['CONFIG_NOVA_NETWORK_FIXEDRANGE'].split('/')[1]
        net_size = 2 ** (32 - int(routing_prefix))
        config['CONFIG_NOVA_NETWORK_FIXEDSIZE'] = str(net_size)

        manifestfile = "%s_nova.pp" % host
        manifestdata = getManifestTemplate("nova_network")
        # Restart libvirt if we deploy nova network on compute
        if host in compute_hosts:
            manifestdata += getManifestTemplate("nova_network_libvirt")

        # in multihost mode each compute host runs nova-api-metadata
        if multihost and host != api_host and host in compute_hosts:
            manifestdata += getManifestTemplate("nova_metadata")
        appendManifestFile(manifestfile, manifestdata)


def create_sched_manifest(config, messages):
    manifestfile = "%s_nova.pp" % config['CONFIG_CONTROLLER_HOST']
    if config['CONFIG_IRONIC_INSTALL'] == 'y':
        manifestdata = getManifestTemplate("nova_sched_ironic.pp")
        ram_alloc = '1.0'
        config['CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO'] = ram_alloc
        manifestdata += getManifestTemplate("nova_sched.pp")
    else:
        manifestdata = getManifestTemplate("nova_sched.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_vncproxy_manifest(config, messages):
    if config["CONFIG_HORIZON_SSL"] == 'y':
        if config["CONFIG_VNC_SSL_CERT"]:
            ssl_cert_file = config["CONFIG_VNC_SSL_CERT"]
            ssl_key_file = config["CONFIG_VNC_SSL_KEY"]
            if not os.path.exists(ssl_cert_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_cert_file)

            if not os.path.exists(ssl_key_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_key_file)

            final_cert = open(ssl_cert_file, 'rt').read()
            final_key = open(ssl_key_file, 'rt').read()
            deliver_ssl_file(final_cert, ssl_cert_file, config['CONFIG_CONTROLLER_HOST'])
            deliver_ssl_file(final_key, ssl_key_file, config['CONFIG_CONTROLLER_HOST'])

        else:
            config["CONFIG_VNC_SSL_CERT"] = '/etc/pki/tls/certs/ssl_vnc.crt'
            config["CONFIG_VNC_SSL_KEY"] = '/etc/pki/tls/private/ssl_vnc.key'
            ssl_key_file = config["CONFIG_VNC_SSL_KEY"]
            ssl_cert_file = config["CONFIG_VNC_SSL_CERT"]
            ssl_host = config['CONFIG_CONTROLLER_HOST']
            service = 'vnc'
            generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                              ssl_cert_file)

    manifestfile = "%s_nova.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("nova_vncproxy")
    appendManifestFile(manifestfile, manifestdata)


def create_common_manifest(config, messages):
    global compute_hosts, network_hosts
    network_type = (config['CONFIG_NEUTRON_INSTALL'] == "y" and
                    'neutron' or 'nova')
    network_multi = len(network_hosts) > 1
    dbacces_hosts = set([config.get('CONFIG_CONTROLLER_HOST')])
    dbacces_hosts |= network_hosts

    for manifestfile, marker in manifestfiles.getFiles():
        pw_in_sqlconn = False
        if manifestfile.endswith("_nova.pp"):
            host, manifest = manifestfile.split('_', 1)
            host = host.strip()

            if host in compute_hosts and host not in dbacces_hosts:
                # we should omit password in case we are installing only
                # nova-compute to the host
                perms = "nova"
                pw_in_sqlconn = False
            else:
                perms = "nova:%s" % config['CONFIG_NOVA_DB_PW']
                pw_in_sqlconn = True

            mariadb_host_url = config['CONFIG_MARIADB_HOST_URL']
            sqlconn = "mysql://%s@%s/nova" % (perms, mariadb_host_url)
            if pw_in_sqlconn:
                config['CONFIG_NOVA_SQL_CONN_PW'] = sqlconn
            else:
                config['CONFIG_NOVA_SQL_CONN_NOPW'] = sqlconn

            # for nova-network in multihost mode each compute host is metadata
            # host otherwise we use api host
            if (network_type == 'nova' and network_multi and
                    host in compute_hosts):
                metadata = host
            else:
                metadata = config['CONFIG_CONTROLLER_HOST']
            config['CONFIG_NOVA_METADATA_HOST'] = metadata

            data = getManifestTemplate(get_mq(config, "nova_common"))
            if pw_in_sqlconn:
                data += getManifestTemplate("nova_common_pw")
            else:
                data += getManifestTemplate("nova_common_nopw")
            appendManifestFile(os.path.split(manifestfile)[1], data)

    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        nova_hosts = compute_hosts
        nova_hosts |= set([config.get('CONFIG_CONTROLLER_HOST')])
        ssl_cert_file = config['CONFIG_NOVA_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_nova.crt'
        )
        ssl_key_file = config['CONFIG_NOVA_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_nova.key'
        )
        service = 'nova'
        for host in nova_hosts:
            generate_ssl_cert(config, host, service,
                              ssl_key_file, ssl_cert_file)


def create_neutron_manifest(config, messages):
    if config['CONFIG_NEUTRON_INSTALL'] != "y":
        return

    if config['CONFIG_IRONIC_INSTALL'] == 'y':
        virt_driver = 'nova.virt.firewall.NoopFirewallDriver'
        config['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = virt_driver
    else:
        virt_driver = 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'
        config['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = virt_driver

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_neutron")
            appendManifestFile(os.path.split(manifestfile)[1], data)
