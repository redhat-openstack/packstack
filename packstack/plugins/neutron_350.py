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
Installs and configures Neutron
"""

import re
from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import output_messages
from packstack.installer.utils import split_hosts

from packstack.modules import common
from packstack.modules.documentation import update_params_usage
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import getManifestTemplate
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Neutron Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Neutron"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    conf_params = {
        "NEUTRON": [
            {"CMD_OPTION": "os-neutron-ks-password",
             "PROMPT": "Enter the password for Neutron Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-db-password",
             "PROMPT": "Enter the password for Neutron DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-l3-ext-bridge",
             "PROMPT": ("Enter the ovs bridge the Neutron L3 agent will use "
                        "for external traffic, or 'provider' if using "
                        "provider networks."),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "br-ex",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_L3_EXT_BRIDGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-metadata-pw",
             "PROMPT": "Enter Neutron metadata agent password",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_METADATA_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-lbaas-install",
             "PROMPT": "Should Packstack install Neutron LBaaS",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_LBAAS_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-metering-agent-install",
             "PROMPT": ("Should Packstack install Neutron L3 Metering agent"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_METERING_AGENT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "neutron-fwaas",
             "PROMPT": "Would you like to configure neutron FWaaS?",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_FWAAS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-vpnaas-install",
             "PROMPT": "Would you like to configure neutron VPNaaS?",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_VPNAAS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NEUTRON_LB_AGENT": [
            {"CMD_OPTION": "os-neutron-lb-interface-mappings",
             "PROMPT": ("Enter a comma separated list of interface mappings "
                        "for the Neutron linuxbridge plugin"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NEUTRON_OVS_AGENT": [
            {"CMD_OPTION": "os-neutron-ovs-bridge-mappings",
             "PROMPT": ("Enter a comma separated list of bridge mappings for "
                        "the Neutron openvswitch plugin"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ovs-bridge-interfaces",
             "PROMPT": ("Enter a comma separated list of OVS bridge:interface "
                        "pairs for the Neutron openvswitch plugin"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_OVS_BRIDGE_IFACES",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ovs-bridges-compute",
             "PROMPT": ("Enter a comma separated list of bridges for the "
                        "Neutron OVS plugin in compute nodes. They must "
                        "be included in os-neutron-ovs-bridge-mappings and "
                        "os-neutron-ovs-bridge-interfaces."),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_OVS_BRIDGES_COMPUTE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

        ],

        "NEUTRON_OVS_AGENT_TUNNEL": [
            {"CMD_OPTION": "os-neutron-ovs-tunnel-if",
             "PROMPT": ("Enter interface with IP to override the default "
                        "tunnel local_ip"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_OVS_TUNNEL_IF",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ovs-tunnel-subnets",
             "PROMPT": ("Enter comma separated list of subnets used for "
                        "tunneling to make them allowed by IP filtering."),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_OVS_TUNNEL_SUBNETS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NEUTRON_OVS_AGENT_VXLAN": [
            {"CMD_OPTION": "os-neutron-ovs-vxlan-udp-port",
             "CONF_NAME": "CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT",
             "PROMPT": "Enter VXLAN UDP port number",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_port],
             "DEFAULT_VALUE": 4789,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "NEUTRON_ML2_PLUGIN": [
            {"CMD_OPTION": "os-neutron-ml2-type-drivers",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_TYPE_DRIVERS",
             "PROMPT": ("Enter a comma separated list of network type driver "
                        "entrypoints"),
             "OPTION_LIST": ["local", "flat", "vlan", "gre", "vxlan"],
             "VALIDATORS": [validators.validate_multi_options],
             "DEFAULT_VALUE": "vxlan",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-tenant-network-types",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES",
             "PROMPT": ("Enter a comma separated ordered list of "
                        "network_types to allocate as tenant networks"),
             "OPTION_LIST": ["local", "vlan", "gre", "vxlan"],
             "VALIDATORS": [validators.validate_multi_options],
             "DEFAULT_VALUE": "vxlan",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-mechanism-drivers",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS",
             "PROMPT": ("Enter a comma separated ordered list of networking "
                        "mechanism driver entrypoints"),
             "OPTION_LIST": ["logger", "test", "linuxbridge", "openvswitch",
                             "hyperv", "ncs", "arista", "cisco_nexus",
                             "mlnx", "l2population", "sriovnicswitch"],
             "VALIDATORS": [validators.validate_multi_options],
             "DEFAULT_VALUE": "openvswitch",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-flat-networks",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_FLAT_NETWORKS",
             "PROMPT": ("Enter a comma separated  list of physical_network "
                        "names with which flat networks can be created"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "*",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-vlan-ranges",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_VLAN_RANGES",
             "PROMPT": ("Enter a comma separated list of physical_network "
                        "names usable for VLAN"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-tunnel-id-ranges",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES",
             "PROMPT": ("Enter a comma separated list of <tun_min>:<tun_max> "
                        "tuples enumerating ranges of GRE tunnel IDs that "
                        "are available for tenant network allocation"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-vxlan-group",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_VXLAN_GROUP",
             "PROMPT": "Enter a multicast group for VXLAN",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-vni-ranges",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_VNI_RANGES",
             "PROMPT": ("Enter a comma separated list of <vni_min>:<vni_max> "
                        "tuples enumerating ranges of VXLAN VNI IDs that are "
                        "available for tenant network allocation"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "10:100",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            # We need to ask for this only in case of ML2 plugins
            {"CMD_OPTION": "os-neutron-l2-agent",
             "PROMPT": ("Enter the name of the L2 agent to be used "
                        "with Neutron"),
             "OPTION_LIST": ["linuxbridge", "openvswitch"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "openvswitch",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_L2_AGENT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "os-neutron-ml2-supported-pci-vendor-devs",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_SUPPORTED_PCI_VENDOR_DEVS",
             "PROMPT": ("Enter a comma separated list of supported PCI "
                        "vendor devices, defined by vendor_id:product_id "
                        "according to the PCI ID Repository."),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": ['15b3:1004', '8086:10ca'],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-sriov-agent-required",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_SRIOV_AGENT_REQUIRED",
             "PROMPT": ("Set to y if the sriov agent is required"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-sriov-interface-mappings",
             "PROMPT": ("Enter a comma separated list of interface mappings "
                        "for the Neutron ML2 sriov agent"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NEUTRON_ML2_SRIOV_INTERFACE_MAPPINGS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
    }
    update_params_usage(basedefs.PACKSTACK_DOC, conf_params)
    conf_groups = [
        {"GROUP_NAME": "NEUTRON",
         "DESCRIPTION": "Neutron config",
         "PRE_CONDITION": "CONFIG_NEUTRON_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NEUTRON_ML2_PLUGIN",
         "DESCRIPTION": "Neutron ML2 plugin config",
         "PRE_CONDITION": neutron_install,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NEUTRON_LB_AGENT",
         "DESCRIPTION": "Neutron LB agent config",
         "PRE_CONDITION": use_ml2_with_linuxbridge,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NEUTRON_OVS_AGENT",
         "DESCRIPTION": "Neutron OVS agent config",
         "PRE_CONDITION": use_ml2_with_ovs,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NEUTRON_OVS_AGENT_TUNNEL",
         "DESCRIPTION": "Neutron OVS agent config for tunnels",
         "PRE_CONDITION": use_ml2_with_ovs,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "NEUTRON_OVS_AGENT_VXLAN",
         "DESCRIPTION": "Neutron OVS agent config for VXLAN",
         "PRE_CONDITION": use_openvswitch_vxlan,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in conf_groups:
        params = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_NEUTRON_INSTALL'] != 'y':
        return
    if config['CONFIG_IRONIC_INSTALL'] == 'y':
        config['CONFIG_NEUTRON_ML2_TYPE_DRIVERS'] += ', flat'
        config['CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES'] += ', flat'
        if 'openvswitch' not in config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS']:
            config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS'] += 'openvswitch'
        config['CONFIG_NEUTRON_ML2_FLAT_NETWORKS'] = 'physnet1'

    if use_ml2_with_sriovnicswitch(config):
        if ('openvswitch' not in config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS']
                and 'linuxbridge' not in
                config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS']):
            config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS'] += ', openvswitch'

    plugin_db = 'neutron'
    plugin_path = 'neutron.plugins.ml2.plugin.Ml2Plugin'
    # values modification
    for key in ('CONFIG_NEUTRON_ML2_TYPE_DRIVERS',
                'CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES',
                'CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS',
                'CONFIG_NEUTRON_ML2_FLAT_NETWORKS',
                'CONFIG_NEUTRON_ML2_VLAN_RANGES',
                'CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES',
                'CONFIG_NEUTRON_ML2_VNI_RANGES'):
        if config[key] == '':
            config[key] = []
        else:
            config[key] = [i.strip() for i in config[key].split(',') if i]
    key = 'CONFIG_NEUTRON_ML2_VXLAN_GROUP'
    config[key] = "%s" % config[key] if config[key] else ''

    config['CONFIG_NEUTRON_L2_DBNAME'] = plugin_db
    config['CONFIG_NEUTRON_CORE_PLUGIN'] = plugin_path

    global api_hosts, network_hosts, compute_hosts, q_hosts
    api_hosts = split_hosts(config['CONFIG_CONTROLLER_HOST'])
    network_hosts = split_hosts(config['CONFIG_NETWORK_HOSTS'])
    compute_hosts = set()
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        compute_hosts = split_hosts(config['CONFIG_COMPUTE_HOSTS'])
    q_hosts = api_hosts | network_hosts | compute_hosts

    if config['CONFIG_NEUTRON_ML2_SRIOV_AGENT_REQUIRED'] == 'y':
        config['CONFIG_NEUTRON_ML2_SRIOV_AGENT_REQUIRED'] = True
    else:
        config['CONFIG_NEUTRON_ML2_SRIOV_AGENT_REQUIRED'] = False

    neutron_steps = [
        {'title': 'Adding Neutron VPNaaS Agent manifest entries',
         'functions': [create_vpnaas_manifests]},
        {'title': 'Adding Neutron FWaaS Agent manifest entries',
         'functions': [create_fwaas_manifests]},
        {'title': 'Adding Neutron LBaaS Agent manifest entries',
         'functions': [create_lbaas_manifests]},
        {'title': 'Adding Neutron API manifest entries',
         'functions': [create_manifests]},
        {'title': 'Adding Neutron Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Neutron L3 manifest entries',
         'functions': [create_l3_manifests]},
        {'title': 'Adding Neutron L2 Agent manifest entries',
         'functions': [create_l2_agent_manifests]},
        {'title': 'Adding Neutron DHCP Agent manifest entries',
         'functions': [create_dhcp_manifests]},
        {'title': 'Adding Neutron Metering Agent manifest entries',
         'functions': [create_metering_agent_manifests]},
        {'title': 'Adding Neutron Metadata Agent manifest entries',
         'functions': [create_metadata_manifests]},
        {'title': 'Adding Neutron SR-IOV Switch Agent manifest entries',
         'functions': [create_sriovnicswitch_manifests]},
        {'title': 'Checking if NetworkManager is enabled and running',
         'functions': [check_nm_status]},
    ]
    controller.addSequence("Installing OpenStack Neutron", [], [],
                           neutron_steps)


# ------------------------- helper functions -------------------------

def neutron_install(config):
    return config['CONFIG_NEUTRON_INSTALL'] == 'y'


def use_ml2_with_linuxbridge(config):
    ml2_used = (neutron_install(config) and
                config["CONFIG_NEUTRON_L2_AGENT"] == 'linuxbridge')
    return ml2_used


def use_ml2_with_ovs(config):
    return (neutron_install(config) and
            config["CONFIG_NEUTRON_L2_AGENT"] == 'openvswitch')


def use_openvswitch_vxlan(config):
    ml2_vxlan = (
        use_ml2_with_ovs(config) and
        'vxlan' in config['CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES']
    )
    return ml2_vxlan


def use_openvswitch_gre(config):
    ml2_vxlan = (
        use_ml2_with_ovs(config) and
        'gre' in config['CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES']
    )
    return ml2_vxlan


def use_ml2_with_sriovnicswitch(config):
    ml2_sriovnic = (
        use_ml2_with_ovs(config) and
        'sriovnicswitch' in config['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS']
    )
    return ml2_sriovnic


def get_if_driver(config):
    agent = config['CONFIG_NEUTRON_L2_AGENT']
    if agent == "openvswitch":
        return 'neutron.agent.linux.interface.OVSInterfaceDriver'
    elif agent == 'linuxbridge':
        return 'neutron.agent.linux.interface.BridgeInterfaceDriver'


def find_mapping(haystack, needle):
    return needle in [x.split(':')[1].strip() for x in get_values(haystack)]


def get_values(val):
    return [x.strip() for x in val.split(',')] if val else []


def tunnel_fw_details(config, host, src):
    key = "neutron_tunnel_%s_%s" % (host, src)
    fw_details = dict()
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "%s" % src
    fw_details[key]['service_name'] = "neutron tunnel port"
    fw_details[key]['chain'] = "INPUT"
    if use_openvswitch_vxlan(config):
        fw_details[key]['proto'] = 'udp'
        tun_port = ("%s" % config['CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT'])
    else:
        fw_details[key]['proto'] = 'gre'
        tun_port = None
    fw_details[key]['ports'] = tun_port
    return fw_details


# -------------------------- step functions --------------------------

def create_manifests(config, messages):
    global q_hosts

    service_plugins = []
    service_providers = []
    if config['CONFIG_LBAAS_INSTALL'] == 'y':
        lbaas_sp = ('LOADBALANCER:Haproxy:neutron_lbaas.services.loadbalancer.'
                    'drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver'
                    ':default')
        service_plugins.append('lbaas')
        service_providers.append(lbaas_sp)

    # ML2 uses the L3 Router service plugin to implement l3 agent
    service_plugins.append('router')

    if config['CONFIG_NEUTRON_METERING_AGENT_INSTALL'] == 'y':
        service_plugins.append('metering')

    if config['CONFIG_NEUTRON_FWAAS'] == 'y':
        service_plugins.append('firewall')

    if config['CONFIG_NEUTRON_VPNAAS'] == 'y':
        service_plugins.append('vpnaas')
        vpnaas_sp = ('VPN:libreswan:neutron_vpnaas.services.vpn.'
                     'service_drivers.ipsec.IPsecVPNDriver:default')
        service_providers.append(vpnaas_sp)

    config['SERVICE_PLUGINS'] = (service_plugins if service_plugins
                                 else 'undef')

    config['SERVICE_PROVIDERS'] = (service_providers if service_providers
                                   else [])

    config['FIREWALL_DRIVER'] = ("neutron.agent.linux.iptables_firewall."
                                 "OVSHybridIptablesFirewallDriver")

    plugin_manifest = 'neutron_ml2_plugin'

    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_cert_file = config['CONFIG_NEUTRON_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_neutron.crt'
        )
        ssl_key_file = config['CONFIG_NEUTRON_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_neutron.key'
        )
        service = 'neutron'

    for host in q_hosts:
        if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
            generate_ssl_cert(config, host, service, ssl_key_file,
                              ssl_cert_file)

        manifest_file = "%s_neutron.pp" % (host,)
        manifest_data = getManifestTemplate("neutron")
        manifest_data += getManifestTemplate(get_mq(config, "neutron"))
        appendManifestFile(manifest_file, manifest_data, 'neutron')

        if host in api_hosts:
            manifest_file = "%s_neutron.pp" % (host,)
            manifest_data = getManifestTemplate("neutron_api")
            if config['CONFIG_NOVA_INSTALL'] == 'y':
                template_name = "neutron_notifications"
                manifest_data += getManifestTemplate(template_name)

            # Set up any l2 plugin configs we need only on neutron api nodes
            # XXX I am not completely sure about this, but it seems necessary:
            manifest_data += getManifestTemplate(plugin_manifest)

            # Firewall
            fw_details = dict()
            key = "neutron_server_%s" % host
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "ALL"
            fw_details[key]['service_name'] = "neutron server"
            fw_details[key]['chain'] = "INPUT"
            fw_details[key]['ports'] = ['9696']
            fw_details[key]['proto'] = "tcp"
            config['FIREWALL_NEUTRON_SERVER_RULES'] = fw_details

            manifest_data += createFirewallResources(
                'FIREWALL_NEUTRON_SERVER_RULES'
            )
            appendManifestFile(manifest_file, manifest_data, 'neutron')

        # We also need to open VXLAN/GRE port for agent
        manifest_data = ""
        if use_openvswitch_vxlan(config) or use_openvswitch_gre(config):
            if config['CONFIG_IP_VERSION'] == 'ipv6':
                msg = output_messages.WARN_IPV6_OVS
                messages.append(utils.color_text(msg % host, 'red'))

            if (config['CONFIG_NEUTRON_OVS_TUNNEL_SUBNETS']):
                tunnel_subnets = map(
                    str.strip,
                    config['CONFIG_NEUTRON_OVS_TUNNEL_SUBNETS'].split(',')
                )
                for subnet in tunnel_subnets:
                    cf_fw_nt_key = ("FIREWALL_NEUTRON_TUNNEL_RULES_%s_%s"
                                    % (host, subnet))
                    config[cf_fw_nt_key] = tunnel_fw_details(config,
                                                             host, subnet)
                    manifest_data += createFirewallResources(cf_fw_nt_key)
            else:
                for n_host in network_hosts | compute_hosts:
                    cf_fw_nt_key = ("FIREWALL_NEUTRON_TUNNEL_RULES_%s_%s"
                                    % (host, n_host))
                    if config['CONFIG_NEUTRON_OVS_TUNNEL_IF']:
                        if config['CONFIG_USE_SUBNETS'] == 'y':
                            iface = common.cidr_to_ifname(
                                config['CONFIG_NEUTRON_OVS_TUNNEL_IF'],
                                n_host, config)
                        else:
                            iface = config['CONFIG_NEUTRON_OVS_TUNNEL_IF']
                        ifip = ("ipaddress_%s" % iface)
                        ifip = re.sub('[\.\-\:]', '_', ifip)
                        try:
                            src_host = config['HOST_DETAILS'][n_host][ifip]
                        except KeyError:
                            raise KeyError('Couldn\'t detect ipaddress of '
                                           'interface %s on node %s' %
                                           (iface, n_host))
                    else:
                        src_host = n_host
                    config[cf_fw_nt_key] = tunnel_fw_details(config,
                                                             host, src_host)
                    manifest_data += createFirewallResources(cf_fw_nt_key)

            appendManifestFile(manifest_file, manifest_data, 'neutron')


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_neutron")
    appendManifestFile(manifestfile, manifestdata)


def create_l3_manifests(config, messages):
    global network_hosts

    if config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] == 'provider':
        config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = ''

    for host in network_hosts:
        config['CONFIG_NEUTRON_L3_HOST'] = host
        config['CONFIG_NEUTRON_L3_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_l3")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + '\n')

        if config['CONFIG_NEUTRON_L2_AGENT'] == 'openvswitch':
            ext_bridge = config['CONFIG_NEUTRON_L3_EXT_BRIDGE']
            mapping = find_mapping(
                config['CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'],
                ext_bridge) if ext_bridge else None
            if (ext_bridge and not mapping):
                config['CONFIG_NEUTRON_OVS_BRIDGE'] = ext_bridge
                manifestdata = getManifestTemplate('neutron_ovs_bridge')
                appendManifestFile(manifestfile, manifestdata + '\n')


def create_dhcp_manifests(config, messages):
    global network_hosts

    for host in network_hosts:
        config["CONFIG_NEUTRON_DHCP_HOST"] = host
        config['CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'] = get_if_driver(config)
        if use_openvswitch_vxlan(config) or use_openvswitch_gre(config):
            manifest_data = getManifestTemplate("neutron_dhcp_mtu")
        else:
            manifest_data = getManifestTemplate("neutron_dhcp")
        manifest_file = "%s_neutron.pp" % (host,)
        # Firewall Rules for dhcp in
        fw_details = dict()
        key = "neutron_dhcp_in_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "ALL"
        fw_details[key]['service_name'] = "neutron dhcp in"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['67']
        fw_details[key]['proto'] = "udp"
        config['FIREWALL_NEUTRON_DHCPIN_RULES'] = fw_details
        manifest_data += createFirewallResources(
            'FIREWALL_NEUTRON_DHCPIN_RULES'
        )

        # Firewall Rules for dhcp out
        fw_details = dict()
        key = "neutron_dhcp_out_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "ALL"
        fw_details[key]['service_name'] = "neutron dhcp out"
        fw_details[key]['chain'] = "OUTPUT"
        fw_details[key]['ports'] = ['68']
        fw_details[key]['proto'] = "udp"
        config['FIREWALL_NEUTRON_DHCPOUT_RULES'] = fw_details
        manifest_data += createFirewallResources(
            'FIREWALL_NEUTRON_DHCPOUT_RULES'
        )

        appendManifestFile(manifest_file, manifest_data, 'neutron')


def create_fwaas_manifests(config, messages):
    global network_hosts

    if not config['CONFIG_NEUTRON_FWAAS'] == 'y':
        return

    for host in network_hosts:
        manifestdata = getManifestTemplate("neutron_fwaas")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_vpnaas_manifests(config, messages):
    global network_hosts

    if config['CONFIG_NEUTRON_VPNAAS'] != 'y':
        return

    for host in network_hosts:
        manifestdata = getManifestTemplate("neutron_vpnaas")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_lbaas_manifests(config, messages):
    global network_hosts

    if not config['CONFIG_LBAAS_INSTALL'] == 'y':
        return

    for host in network_hosts:
        config['CONFIG_NEUTRON_LBAAS_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_lbaas")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_metering_agent_manifests(config, messages):
    global network_hosts

    if not config['CONFIG_NEUTRON_METERING_AGENT_INSTALL'] == 'y':
        return

    for host in network_hosts:
        config['CONFIG_NEUTRON_METERING_IFCE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_metering_agent")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_l2_agent_manifests(config, messages):
    global network_hosts, compute_hosts

    agent = config["CONFIG_NEUTRON_L2_AGENT"]

    # CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS will be available only for ML2
    # plugin deployment, but we need CONFIG_NEUTRON_USE_L2POPULATION also
    # for other plugin template generation
    if ('l2population' in
            config.get('CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS', [])):
        config['CONFIG_NEUTRON_USE_L2POPULATION'] = True
    else:
        config['CONFIG_NEUTRON_USE_L2POPULATION'] = False

    if agent == "openvswitch":
        ovs_type = 'CONFIG_NEUTRON_ML2_TYPE_DRIVERS'
        ovs_type = config.get(ovs_type, 'local')
        tunnel = use_openvswitch_vxlan(config) or use_openvswitch_gre(config)
        config["CONFIG_NEUTRON_OVS_TUNNELING"] = tunnel
        tunnel_types = set(ovs_type) & set(['gre', 'vxlan'])
        config["CONFIG_NEUTRON_OVS_TUNNEL_TYPES"] = list(tunnel_types)
        template_name = "neutron_ovs_agent"

        bm_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"])
        iface_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"])

        # The CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS parameter contains a
        # comma-separated list of bridge mappings. Since the puppet module
        # expects this parameter to be an array, this parameter must be
        # properly formatted by packstack, then consumed by the puppet module.
        # For example, the input string 'A, B' should formatted as '['A','B']'.
        config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"] = bm_arr
        config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"] = []

        # Bridge configuration and mappings for compute nodes can be different.
        # Parameter CONFIG_NEUTRON_OVS_BRIDGES_COMPUTE contains the list of
        # bridge names, included in bridge mappings and bridge interfaces, that
        # must be created in compute nodes.
        brd_arr_cmp = get_values(config["CONFIG_NEUTRON_OVS_BRIDGES_COMPUTE"])
        if_arr_cmp = []
        mapp_arr_cmp = []
        for brd in brd_arr_cmp:
            if_arr_cmp.append(common.find_pair_with(iface_arr, brd, 0))
            mapp_arr_cmp.append(common.find_pair_with(bm_arr, brd, 1))

        config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS_COMPUTE"] = mapp_arr_cmp
        config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES_COMPUTE"] = []

    elif agent == "linuxbridge":
        host_var = 'CONFIG_NEUTRON_LB_HOST'
        template_name = 'neutron_lb_agent'
    else:
        raise KeyError("Unknown layer2 agent")

    no_local_types = set(ovs_type) & set(['gre', 'vxlan', 'vlan', 'flat'])
    no_tunnel_types = set(ovs_type) & set(['vlan', 'flat'])

    for host in network_hosts | compute_hosts:
        manifestfile = "%s_neutron.pp" % (host,)
        manifestdata = "$cfg_neutron_ovs_host = '%s'\n" % host
        # NICs connected to OVS bridges can be required in network nodes if
        # vlan, flat, vxlan or gre are enabled. For compute nodes, they are
        # only required if vlan or flat are enabled.
        if (
            agent == "openvswitch" and (
                (host in network_hosts and no_local_types)
                or no_tunnel_types)
        ):
            if config['CONFIG_USE_SUBNETS'] == 'y':
                iface_arr = [
                    common.cidr_to_ifname(i, host, config) for i in iface_arr
                ]
                if_arr_cmp = [
                    common.cidr_to_ifname(i, host, config) for i in if_arr_cmp
                ]
            config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"] = iface_arr
            config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES_COMPUTE"] = if_arr_cmp
            manifestdata += "$create_bridges = true\n"
        else:
            manifestdata += "$create_bridges = false\n"
        is_network_host = str(host in network_hosts).lower()
        manifestdata += "$network_host = %s\n" % is_network_host
        manifestdata += getManifestTemplate(template_name)
        appendManifestFile(manifestfile, manifestdata + "\n")
        # Additional configurations required for compute hosts and
        # network hosts.
        manifestdata = getManifestTemplate('neutron_bridge_module')
        appendManifestFile(manifestfile, manifestdata + '\n')


def create_sriovnicswitch_manifests(config, messages):
    global compute_hosts

    if not use_ml2_with_sriovnicswitch(config):
        return

    for host in compute_hosts:
        manifestdata = getManifestTemplate("neutron_sriov")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_metadata_manifests(config, messages):
    global network_hosts
    if config.get('CONFIG_NOVA_INSTALL') == 'n':
        return
    for host in network_hosts:
        config['CONFIG_NEUTRON_METADATA_HOST'] = host
        manifestdata = getManifestTemplate('neutron_metadata')
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def check_nm_status(config, messages):
    hosts_with_nm = []
    for host in common.filtered_hosts(config):
        server = utils.ScriptRunner(host)
        server.append("systemctl")
        rc, out = server.execute(can_fail=False)
        server.clear()

        if rc < 1:
            server.append("systemctl is-enabled NetworkManager")
            rc, is_enabled = server.execute(can_fail=False)
            is_enabled = is_enabled.strip("\n ")
            server.clear()

            server.append("systemctl is-active NetworkManager")
            rc, is_active = server.execute(can_fail=False)
            is_active = is_active.strip("\n ")

            if is_enabled == "enabled" or is_active == "active":
                hosts_with_nm.append(host)
        else:
            server.clear()
            server.append("service NetworkManager status")
            rc, out = server.execute(can_fail=False)

            if rc < 1:
                hosts_with_nm.append(host)

        server.clear()

    if hosts_with_nm:
        hosts_list = ', '.join("%s" % x for x in hosts_with_nm)
        msg = output_messages.WARN_NM_ENABLED
        messages.append(utils.color_text(msg % hosts_list, 'yellow'))
