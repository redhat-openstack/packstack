# -*- coding: utf-8 -*-

"""
Installs and configures Neutron
"""

from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import output_messages
from packstack.installer.utils import split_hosts

from packstack.modules.common import filtered_hosts
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


# ------------- Neutron Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Neutron"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    conf_params = {
        "NEUTRON": [
            {"CMD_OPTION": "os-neutron-ks-password",
             "USAGE": ("The password to use for Neutron to authenticate "
                       "with Keystone"),
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
             "USAGE": "The password to use for Neutron to access DB",
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
             "USAGE": ("The name of the ovs bridge (or empty for linuxbridge)"
                       " that the Neutron L3 agent will use for external "
                       " traffic, or 'provider' using provider networks. "),
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
             "USAGE": "Neutron metadata agent password",
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
             "USAGE": ("Set to 'y' if you would like Packstack to install "
                       "Neutron LBaaS"),
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
             "USAGE": ("Set to 'y' if you would like Packstack to install "
                       "Neutron L3 Metering agent"),
             "PROMPT": ("Should Packstack install Neutron L3 Metering agent"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_METERING_AGENT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "neutron-fwaas",
             "USAGE": ("Whether to configure neutron Firewall as a Service"),
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
        ],

        "NEUTRON_LB_AGENT": [
            {"CMD_OPTION": "os-neutron-lb-interface-mappings",
             "USAGE": ("A comma separated list of interface mappings for the "
                       "Neutron linuxbridge plugin (eg. physnet1:eth1,"
                       "physnet2:eth2,physnet3:eth3)"),
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
             "USAGE": ("A comma separated list of bridge mappings for the "
                       "Neutron openvswitch plugin (eg. physnet1:br-eth1,"
                       "physnet2:br-eth2,physnet3:br-eth3)"),
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
             "USAGE": ("A comma separated list of colon-separated OVS "
                       "bridge:interface pairs. The interface will be added "
                       "to the associated bridge."),
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
        ],

        "NEUTRON_OVS_AGENT_TUNNEL": [
            {"CMD_OPTION": "os-neutron-ovs-tunnel-if",
             "USAGE": ("The interface for the OVS tunnel. Packstack will "
                       "override the IP address used for tunnels on this "
                       "hypervisor to the IP found on the specified interface."
                       " (eg. eth1)"),
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
        ],

        "NEUTRON_OVS_AGENT_VXLAN": [
            {"CMD_OPTION": "os-neutron-ovs-vxlan-udp-port",
             "CONF_NAME": "CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT",
             "USAGE": "VXLAN UDP port",
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
             "USAGE": ("A comma separated list of network type driver "
                       "entrypoints to be loaded from the "
                       "neutron.ml2.type_drivers namespace."),
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
             "USAGE": ("A comma separated ordered list of network_types to "
                       "allocate as tenant networks. The value 'local' is "
                       "only useful for single-box testing but provides no "
                       "connectivity between hosts."),
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
             "USAGE": ("A comma separated ordered list of networking "
                       "mechanism driver entrypoints to be loaded from the "
                       "neutron.ml2.mechanism_drivers namespace."),
             "PROMPT": ("Enter a comma separated ordered list of networking "
                        "mechanism driver entrypoints"),
             "OPTION_LIST": ["logger", "test", "linuxbridge", "openvswitch",
                             "hyperv", "ncs", "arista", "cisco_nexus",
                             "l2population"],
             "VALIDATORS": [validators.validate_multi_options],
             "DEFAULT_VALUE": "openvswitch",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-ml2-flat-networks",
             "CONF_NAME": "CONFIG_NEUTRON_ML2_FLAT_NETWORKS",
             "USAGE": ("A comma separated  list of physical_network names "
                       "with which flat networks can be created. Use * to "
                       "allow flat networks with arbitrary physical_network "
                       "names."),
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
             "USAGE": ("A comma separated list of <physical_network>:"
                       "<vlan_min>:<vlan_max> or <physical_network> "
                       "specifying physical_network names usable for VLAN "
                       "provider and tenant networks, as well as ranges of "
                       "VLAN tags on each available for allocation to tenant "
                       "networks."),
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
             "USAGE": ("A comma separated list of <tun_min>:<tun_max> tuples "
                       "enumerating ranges of GRE tunnel IDs that are "
                       "available for tenant network allocation. Should be "
                       "an array with tun_max +1 - tun_min > 1000000"),
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
             "USAGE": ("Multicast group for VXLAN. If unset, disables VXLAN "
                       "enable sending allocate broadcast traffic to this "
                       "multicast group. When left unconfigured, will disable "
                       "multicast VXLAN mode. Should be an Multicast IP "
                       "(v4 or v6) address."),
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
             "USAGE": ("A comma separated list of <vni_min>:<vni_max> tuples "
                       "enumerating ranges of VXLAN VNI IDs that are "
                       "available for tenant network allocation. Min value "
                       "is 0 and Max value is 16777215."),
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
             "USAGE": "The name of the L2 agent to be used with Neutron",
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
        ],
    }

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

    neutron_steps = [
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
        {'title': 'Adding Neutron LBaaS Agent manifest entries',
         'functions': [create_lbaas_manifests]},
        {'title': 'Adding Neutron Metering Agent manifest entries',
         'functions': [create_metering_agent_manifests]},
        {'title': 'Adding Neutron Metadata Agent manifest entries',
         'functions': [create_metadata_manifests]},
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


# -------------------------- step functions --------------------------

def create_manifests(config, messages):
    global q_hosts

    service_plugins = []
    if config['CONFIG_LBAAS_INSTALL'] == 'y':
        service_plugins.append(
            'neutron.services.loadbalancer.plugin.LoadBalancerPlugin'
        )

    # ML2 uses the L3 Router service plugin to implement l3 agent
    service_plugins.append(
        'neutron.services.l3_router.l3_router_plugin.L3RouterPlugin'
    )

    if config['CONFIG_NEUTRON_METERING_AGENT_INSTALL'] == 'y':
        service_plugins.append(
            'neutron.services.metering.metering_plugin.MeteringPlugin'
        )

    if config['CONFIG_NEUTRON_FWAAS'] == 'y':
        service_plugins.append(
            'neutron.services.firewall.fwaas_plugin.FirewallPlugin'
        )

    config['SERVICE_PLUGINS'] = (service_plugins if service_plugins
                                 else 'undef')

    plugin_manifest = 'neutron_ml2_plugin.pp'

    for host in q_hosts:
        manifest_file = "%s_neutron.pp" % (host,)
        manifest_data = getManifestTemplate("neutron.pp")
        manifest_data += getManifestTemplate(get_mq(config, "neutron"))
        appendManifestFile(manifest_file, manifest_data, 'neutron')

        if host in api_hosts:
            manifest_file = "%s_neutron.pp" % (host,)
            manifest_data = getManifestTemplate("neutron_api.pp")
            if config['CONFIG_NOVA_INSTALL'] == 'y':
                template_name = "neutron_notifications.pp"
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
        if use_openvswitch_vxlan(config) or use_openvswitch_gre(config):
            fw_details = dict()
            key = "neutron_tunnel"
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "ALL"
            fw_details[key]['service_name'] = "neutron tunnel port"
            fw_details[key]['chain'] = "INPUT"

            if use_openvswitch_vxlan(config):
                fw_details[key]['proto'] = 'udp'
                tun_port = "%s" % config['CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT']
            else:
                fw_details[key]['proto'] = 'gre'
                tun_port = None

            fw_details[key]['ports'] = tun_port
            config['FIREWALL_NEUTRON_TUNNEL_RULES'] = fw_details

            manifest_data = createFirewallResources(
                'FIREWALL_NEUTRON_TUNNEL_RULES'
            )
            appendManifestFile(manifest_file, manifest_data, 'neutron')


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_neutron.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_l3_manifests(config, messages):
    global network_hosts

    if config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] == 'provider':
        config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = ''

    for host in network_hosts:
        config['CONFIG_NEUTRON_L3_HOST'] = host
        config['CONFIG_NEUTRON_L3_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_l3.pp")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + '\n')

        if config['CONFIG_NEUTRON_L2_AGENT'] == 'openvswitch':
            ext_bridge = config['CONFIG_NEUTRON_L3_EXT_BRIDGE']
            mapping = find_mapping(
                config['CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'],
                ext_bridge) if ext_bridge else None
            if (ext_bridge and not mapping):
                config['CONFIG_NEUTRON_OVS_BRIDGE'] = ext_bridge
                manifestdata = getManifestTemplate('neutron_ovs_bridge.pp')
                appendManifestFile(manifestfile, manifestdata + '\n')

        if config['CONFIG_NEUTRON_FWAAS'] == 'y':
            # manifestfile = "%s_neutron_fwaas.pp" % (host,)
            manifestdata = getManifestTemplate("neutron_fwaas.pp")
            appendManifestFile(manifestfile, manifestdata + '\n')


def create_dhcp_manifests(config, messages):
    global network_hosts

    for host in network_hosts:
        config["CONFIG_NEUTRON_DHCP_HOST"] = host
        config['CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'] = get_if_driver(config)
        if use_openvswitch_vxlan(config) or use_openvswitch_gre(config):
            manifest_data = getManifestTemplate("neutron_dhcp_mtu.pp")
        else:
            manifest_data = getManifestTemplate("neutron_dhcp.pp")
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


def create_lbaas_manifests(config, messages):
    global network_hosts

    if not config['CONFIG_LBAAS_INSTALL'] == 'y':
        return

    for host in network_hosts:
        config['CONFIG_NEUTRON_LBAAS_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_lbaas.pp")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def create_metering_agent_manifests(config, messages):
    global network_hosts

    if not config['CONFIG_NEUTRON_METERING_AGENT_INSTALL'] == 'y':
        return

    for host in network_hosts:
        config['CONFIG_NEUTRON_METERING_IFCE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_metering_agent.pp")
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
        ovs_type = 'CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES'
        ovs_type = config.get(ovs_type, 'local')
        tunnel = use_openvswitch_vxlan(config) or use_openvswitch_gre(config)
        config["CONFIG_NEUTRON_OVS_TUNNELING"] = tunnel
        tunnel_types = set(ovs_type) & set(['gre', 'vxlan'])
        config["CONFIG_NEUTRON_OVS_TUNNEL_TYPES"] = list(tunnel_types)
        template_name = "neutron_ovs_agent.pp"

        bm_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"])
        iface_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"])

        # The CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS parameter contains a
        # comma-separated list of bridge mappings. Since the puppet module
        # expects this parameter to be an array, this parameter must be
        # properly formatted by packstack, then consumed by the puppet module.
        # For example, the input string 'A, B' should formatted as '['A','B']'.
        config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"] = bm_arr
    elif agent == "linuxbridge":
        host_var = 'CONFIG_NEUTRON_LB_HOST'
        template_name = 'neutron_lb_agent.pp'
    else:
        raise KeyError("Unknown layer2 agent")

    for host in network_hosts | compute_hosts:
        manifestfile = "%s_neutron.pp" % (host,)
        manifestdata = "$cfg_neutron_ovs_host = '%s'\n" % host
        manifestdata += getManifestTemplate(template_name)
        appendManifestFile(manifestfile, manifestdata + "\n")
        # neutron ovs port only on network hosts
        if (
            agent == "openvswitch" and (
                (host in network_hosts and tunnel_types)
                or 'vlan' in ovs_type)
        ):
            bridge_key = 'CONFIG_NEUTRON_OVS_BRIDGE'
            iface_key = 'CONFIG_NEUTRON_OVS_IFACE'
            for if_map in iface_arr:
                config[bridge_key], config[iface_key] = if_map.split(':')
                manifestdata = getManifestTemplate("neutron_ovs_port.pp")
                appendManifestFile(manifestfile, manifestdata + "\n")
        # Additional configurations required for compute hosts and
        # network hosts.
        manifestdata = getManifestTemplate('neutron_bridge_module.pp')
        appendManifestFile(manifestfile, manifestdata + '\n')


def create_metadata_manifests(config, messages):
    global network_hosts
    if config.get('CONFIG_NOVA_INSTALL') == 'n':
        return
    for host in network_hosts:
        config['CONFIG_NEUTRON_METADATA_HOST'] = host
        manifestdata = getManifestTemplate('neutron_metadata.pp')
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def check_nm_status(config, messages):
    hosts_with_nm = []
    for host in filtered_hosts(config):
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
