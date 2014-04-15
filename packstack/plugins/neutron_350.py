"""
Installs and configures neutron
"""

import logging
import os
import re
import uuid

from packstack.installer import utils
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-NEUTRON"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    logging.debug("Adding OpenStack Neutron configuration")

    conf_params = {
        "NEUTRON" : [
            {"CMD_OPTION"      : "neutron-server-host",
             "USAGE"           : "The IP addresses of the server on which to install the Neutron server",
             "PROMPT"          : "Enter the IP address of the Neutron server",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_ip, validators.validate_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_SERVER_HOST",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ks-password",
             "USAGE"           : "The password to use for Neutron to authenticate with Keystone",
             "PROMPT"          : "Enter the password for Neutron Keystone access",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_KS_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-db-password",
             "USAGE"           : "The password to use for Neutron to access DB",
             "PROMPT"          : "Enter the password for Neutron DB access",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_DB_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-l3-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Neutron L3 agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Neutron L3 agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_L3_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-l3-ext-bridge",
             "USAGE"           : "The name of the bridge that the Neutron L3 agent will use for external traffic, or 'provider' if using provider networks",
             "PROMPT"          : "Enter the bridge the Neutron L3 agent will use for external traffic, or 'provider' if using provider networks",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "br-ex",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_L3_EXT_BRIDGE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-dhcp-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Neutron DHCP agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install Neutron DHCP agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_DHCP_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-lbaas-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Neutron LBaaS agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install Neutron LBaaS agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_LBAAS_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-l2-plugin",
             "USAGE"           : "The name of the L2 plugin to be used with Neutron",
             "PROMPT"          : "Enter the name of the L2 plugin to be used with Neutron",
             "OPTION_LIST"     : ["linuxbridge", "openvswitch", "ml2"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "openvswitch",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_L2_PLUGIN",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-metadata-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Neutron metadata agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Neutron metadata agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_METADATA_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-metadata-pw",
             "USAGE"           : "A comma separated list of IP addresses on which to install Neutron metadata agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Neutron metadata agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_METADATA_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            ],
        "NEUTRON_LB_PLUGIN" : [
            {"CMD_OPTION"      : "neutron-lb-tenant-network-type",
             "USAGE"           : "The type of network to allocate for tenant networks (eg. vlan, local)",
             "PROMPT"          : "Enter the type of network to allocate for tenant networks",
             "OPTION_LIST"     : ["local", "vlan"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_LB_TENANT_NETWORK_TYPE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-lb-vlan-ranges",
             "USAGE"           : "A comma separated list of VLAN ranges for the Neutron linuxbridge plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999)",
             "PROMPT"          : "Enter a comma separated list of VLAN ranges for the Neutron linuxbridge plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_LB_VLAN_RANGES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_LB_PLUGIN_AND_AGENT" : [
            {"CMD_OPTION"      : "neutron-lb-interface-mappings",
             "USAGE"           : "A comma separated list of interface mappings for the Neutron linuxbridge plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3)",
             "PROMPT"          : "Enter a comma separated list of interface mappings for the Neutron linuxbridge plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_OVS_PLUGIN" : [
            {"CMD_OPTION"      : "neutron-ovs-tenant-network-type",
             "USAGE"           : "Type of network to allocate for tenant networks (eg. vlan, local, gre, vxlan)",
             "PROMPT"          : "Enter the type of network to allocate for tenant networks",
             "OPTION_LIST"     : ["local", "vlan", "gre", "vxlan"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ovs-vlan-ranges",
             "USAGE"           : "A comma separated list of VLAN ranges for the Neutron openvswitch plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999)",
             "PROMPT"          : "Enter a comma separated list of VLAN ranges for the Neutron openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_VLAN_RANGES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_OVS_PLUGIN_AND_AGENT" : [
            {"CMD_OPTION"      : "neutron-ovs-bridge-mappings",
             "USAGE"           : "A comma separated list of bridge mappings for the Neutron openvswitch plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3)",
             "PROMPT"          : "Enter a comma separated list of bridge mappings for the Neutron openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ovs-bridge-interfaces",
             "USAGE"           : "A comma separated list of colon-separated OVS bridge:interface pairs. The interface will be added to the associated bridge.",
             "PROMPT"          : "Enter a comma separated list of OVS bridge:interface pairs for the Neutron openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_BRIDGE_IFACES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_OVS_PLUGIN_TUNNEL" : [
            {"CMD_OPTION"      : "neutron-ovs-tunnel-ranges",
             "USAGE"           : "A comma separated list of tunnel ranges for the Neutron openvswitch plugin (eg. 1:1000)",
             "PROMPT"          : "Enter a comma separated list of tunnel ranges for the Neutron openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_TUNNEL_RANGES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_OVS_PLUGIN_AND_AGENT_TUNNEL" : [
            {"CMD_OPTION"      : "neutron-ovs-tunnel-if",
             "USAGE"           : "The interface for the OVS tunnel. Packstack will override the IP address used for tunnels on this hypervisor to the IP found on the specified interface. (eg. eth1) ",
             "PROMPT"          : "Enter interface with IP to override the default tunnel local_ip",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_TUNNEL_IF",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_OVS_PLUGIN_AND_AGENT_VXLAN" : [
            {"CMD_OPTION"      : "neutron-ovs-vxlan-udp-port",
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT",
             "USAGE"           : "VXLAN UDP port",
             "PROMPT"          : "Enter VXLAN UDP port number",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_port],
             "DEFAULT_VALUE"   : 4789,
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,

             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "NEUTRON_ML2_PLUGIN" : [
            {"CMD_OPTION"      : "neutron-ml2-type-drivers",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_TYPE_DRIVERS",
             "USAGE"           : ("A comma separated list of network type "
                                  "driver entrypoints to be loaded from the "
                                  "neutron.ml2.type_drivers namespace."),
             "PROMPT"          : ("Enter a comma separated list of network "
                                  "type driver entrypoints"),
             "OPTION_LIST"     : ["local", "flat", "vlan", "gre", "vxlan"],
             "VALIDATORS"      : [validators.validate_multi_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-tenant-network-types",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES",
             "USAGE"           : ("A comma separated ordered list of "
                                  "network_types to allocate as tenant "
                                  "networks. The value 'local' is only useful "
                                  "for single-box testing but provides no "
                                  "connectivity between hosts."),
             "PROMPT"          : ("Enter a comma separated ordered list of "
                                  "network_types to allocate as tenant "
                                  "networks"),
             "OPTION_LIST"     : ["local", "vlan", "gre", "vxlan"],
             "VALIDATORS"      : [validators.validate_multi_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-mechanism-drivers",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS",
             "USAGE"           : ("A comma separated ordered list of "
                                  "networking mechanism driver entrypoints "
                                  "to be loaded from the "
                                  "neutron.ml2.mechanism_drivers namespace."),
             "PROMPT"          : ("Enter a comma separated ordered list of "
                                  "networking mechanism driver entrypoints"),
             "OPTION_LIST"     : ["logger", "test", "linuxbridge",
                                  "openvswitch", "hyperv", "ncs", "arista",
                                  "cisco_nexus", "l2population"],
             "VALIDATORS"      : [validators.validate_multi_options],
             "DEFAULT_VALUE"   : "openvswitch",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-flat-networks",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_FLAT_NETWORKS",
             "USAGE"           : ("A comma separated  list of physical_network"
                                  " names with which flat networks can be "
                                  "created. Use * to allow flat networks with "
                                  "arbitrary physical_network names."),
             "PROMPT"          : ("Enter a comma separated  list of "
                                  "physical_network names with which flat "
                                  "networks can be created"),
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "*",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-vlan-ranges",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_VLAN_RANGES",
             "USAGE"           : ("A comma separated list of "
                                  "<physical_network>:<vlan_min>:<vlan_max> "
                                  "or <physical_network> specifying "
                                  "physical_network names usable for VLAN "
                                  "provider and tenant networks, as well as "
                                  "ranges of VLAN tags on each available for "
                                  "allocation to tenant networks."),
             "PROMPT"          : ("Enter a comma separated list of "
                                  "physical_network names usable for VLAN"),
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-tunnel-id-ranges",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES",
             "USAGE"           : ("A comma separated list of <tun_min>:"
                                  "<tun_max> tuples enumerating ranges of GRE "
                                  "tunnel IDs that are available for tenant "
                                  "network allocation. Should be an array with"
                                  " tun_max +1 - tun_min > 1000000"),
             "PROMPT"          : ("Enter a comma separated list of <tun_min>:"
                                  "<tun_max> tuples enumerating ranges of GRE "
                                  "tunnel IDs that are available for tenant "
                                  "network allocation"),
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-vxlan-group",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_VXLAN_GROUP",
             "USAGE"           : ("Multicast group for VXLAN. If unset, "
                                  "disables VXLAN enable sending allocate "
                                  "broadcast traffic to this multicast group. "
                                  "When left unconfigured, will disable "
                                  "multicast VXLAN mode. Should be an "
                                  "Multicast IP (v4 or v6) address."),
             "PROMPT"          : "Enter a multicast group for VXLAN",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ml2-vni-ranges",
             "CONF_NAME"       : "CONFIG_NEUTRON_ML2_VNI_RANGES",
             "USAGE"           : ("A comma separated list of <vni_min>:"
                                  "<vni_max> tuples enumerating ranges of "
                                  "VXLAN VNI IDs that are available for tenant"
                                  " network allocation. Min value is 0 and Max"
                                  " value is 16777215."),
             "PROMPT"          : ("Enter a comma separated list of <vni_min>:"
                                  "<vni_max> tuples enumerating ranges of "
                                  "VXLAN VNI IDs that are available for tenant"
                                  " network allocation"),
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-l2-agent", # We need to ask for this only in case of ML2 plugins
             "USAGE"           : "The name of the L2 agent to be used with Neutron",
             "PROMPT"          : "Enter the name of the L2 agent to be used with Neutron",
             "OPTION_LIST"     : ["linuxbridge", "openvswitch"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "openvswitch",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_L2_AGENT",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        }

    def use_ml2_plugin(config):
        return (config['CONFIG_NEUTRON_INSTALL'] == 'y' and
                config['CONFIG_NEUTRON_L2_PLUGIN'] == 'ml2')

    def use_linuxbridge_plugin(config):
        result = (config['CONFIG_NEUTRON_INSTALL'] == 'y' and
                  config['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge')
        if result:
            config["CONFIG_NEUTRON_L2_AGENT"] = 'linuxbridge'
        return result

    def use_linuxbridge_agent(config):
        ml2_used = (use_ml2_plugin(config) and
                    config["CONFIG_NEUTRON_L2_AGENT"] == 'linuxbridge')
        return use_linuxbridge_plugin(config) or ml2_used

    def use_openvswitch_plugin(config):
        result = (config['CONFIG_NEUTRON_INSTALL'] == 'y' and
                  config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch')
        if result:
            config["CONFIG_NEUTRON_L2_AGENT"] = 'openvswitch'
        return result

    def use_openvswitch_plugin_tunnel(config):
        tun_types = ('gre', 'vxlan')
        return (use_openvswitch_plugin(config) and
                config['CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE'] in tun_types)

    def use_ml2_with_ovs(config):
        return (use_ml2_plugin(config) and
                config["CONFIG_NEUTRON_L2_AGENT"] == 'openvswitch')

    def use_openvswitch_agent(config):
        return use_openvswitch_plugin(config) or use_ml2_with_ovs(config)

    def use_openvswitch_agent_tunnel(config):
        return use_openvswitch_plugin_tunnel(config) or use_ml2_with_ovs(config)

    def use_openvswitch_vxlan(config):
        ovs_vxlan = (
            use_openvswitch_plugin_tunnel(config) and
            config['CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE'] == 'vxlan'
        )
        ml2_vxlan = (
            use_ml2_with_ovs(config) and
            'vxlan' in config['CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES']
        )
        return ovs_vxlan or ml2_vxlan


    conf_groups = [
        { "GROUP_NAME"            : "NEUTRON",
          "DESCRIPTION"           : "Neutron config",
          "PRE_CONDITION"         : "CONFIG_NEUTRON_INSTALL",
          "PRE_CONDITION_MATCH"   : "y",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_ML2_PLUGIN",
          "DESCRIPTION"           : "Neutron ML2 plugin config",
          "PRE_CONDITION"         : use_ml2_plugin,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_LB_PLUGIN",
          "DESCRIPTION"           : "Neutron LB plugin config",
          "PRE_CONDITION"         : use_linuxbridge_plugin,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_LB_PLUGIN_AND_AGENT",
          "DESCRIPTION"           : "Neutron LB agent config",
          "PRE_CONDITION"         : use_linuxbridge_agent,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN",
          "DESCRIPTION"           : "Neutron OVS plugin config",
          "PRE_CONDITION"         : use_openvswitch_plugin,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN_AND_AGENT",
          "DESCRIPTION"           : "Neutron OVS agent config",
          "PRE_CONDITION"         : use_openvswitch_agent,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN_TUNNEL",
          "DESCRIPTION"           : "Neutron OVS plugin config for tunnels",
          "PRE_CONDITION"         : use_openvswitch_plugin_tunnel,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN_AND_AGENT_TUNNEL",
          "DESCRIPTION"           : "Neutron OVS agent config for tunnels",
          "PRE_CONDITION"         : use_openvswitch_agent_tunnel,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN_AND_AGENT_VXLAN",
          "DESCRIPTION"           : "Neutron OVS agent config for VXLAN",
          "PRE_CONDITION"         : use_openvswitch_vxlan,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def get_if_driver(config):
    agent = config['CONFIG_NEUTRON_L2_AGENT']
    if agent == "openvswitch":
        return 'neutron.agent.linux.interface.OVSInterfaceDriver'
    elif agent == 'linuxbridge':
        return 'neutron.agent.linux.interface.BridgeInterfaceDriver'


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_NEUTRON_INSTALL'] != 'y':
        return

    if config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch':
        plugin_db = 'ovs_neutron'
        plugin_path = ('neutron.plugins.openvswitch.ovs_neutron_plugin.'
                       'OVSNeutronPluginV2')
    elif config['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge':
        plugin_db = 'neutron_linux_bridge'
        plugin_path = ('neutron.plugins.linuxbridge.lb_neutron_plugin.'
                       'LinuxBridgePluginV2')
    elif config['CONFIG_NEUTRON_L2_PLUGIN'] == 'ml2':
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
            config[key] = str([i.strip() for i in config[key].split(',') if i])
        key = 'CONFIG_NEUTRON_ML2_VXLAN_GROUP'
        config[key] = "'%s'" % config[key] if config[key] else 'undef'

    config['CONFIG_NEUTRON_L2_DBNAME']  = plugin_db
    config['CONFIG_NEUTRON_CORE_PLUGIN'] = plugin_path

    global api_hosts, l3_hosts, dhcp_hosts, lbaas_hosts, compute_hosts, meta_hosts, q_hosts
    api_hosts = split_hosts(config['CONFIG_NEUTRON_SERVER_HOST'])
    l3_hosts = split_hosts(config['CONFIG_NEUTRON_L3_HOSTS'])
    dhcp_hosts = split_hosts(config['CONFIG_NEUTRON_DHCP_HOSTS'])
    lbaas_hosts = split_hosts(config['CONFIG_NEUTRON_LBAAS_HOSTS'])
    meta_hosts = split_hosts(config['CONFIG_NEUTRON_METADATA_HOSTS'])
    compute_hosts = set()
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        compute_hosts = split_hosts(config['CONFIG_NOVA_COMPUTE_HOSTS'])
    q_hosts = api_hosts | l3_hosts | dhcp_hosts | lbaas_hosts | compute_hosts | meta_hosts

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
        {'title': 'Adding Neutron Metadata Agent manifest entries',
         'functions': [create_metadata_manifests]},
    ]
    controller.addSequence("Installing OpenStack Neutron", [], [],
                           neutron_steps)


def create_manifests(config):
    global q_hosts

    service_plugins = []
    if config['CONFIG_NEUTRON_LBAAS_HOSTS']:
        service_plugins.append(
            'neutron.services.loadbalancer.plugin.LoadBalancerPlugin'
        )
    if config['CONFIG_NEUTRON_L2_PLUGIN'] == 'ml2':
        # ML2 uses the L3 Router service plugin to implement l3 agent
        service_plugins.append(
            'neutron.services.l3_router.l3_router_plugin.L3RouterPlugin'
        )

    config['SERVICE_PLUGINS'] = (str(service_plugins) if service_plugins
                                 else 'undef')

    if config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch':
        nettype = config.get("CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE", "local")
        plugin_manifest = 'neutron_ovs_plugin_%s.pp' % nettype
    elif config['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge':
        plugin_manifest = 'neutron_lb_plugin.pp'
    elif config['CONFIG_NEUTRON_L2_PLUGIN'] == 'ml2':
        plugin_manifest = 'neutron_ml2_plugin.pp'

    # host to which allow neutron server
    allowed_hosts = set(q_hosts)
    if config['CONFIG_CLIENT_INSTALL'] == 'y':
        allowed_hosts.add(config['CONFIG_OSCLIENT_HOST'])
    if config['CONFIG_HORIZON_INSTALL'] == 'y':
        allowed_hosts.add(config['CONFIG_HORIZON_HOST'])
    if config['CONFIG_NOVA_INSTALL'] == 'y':
        allowed_hosts.add(config['CONFIG_NOVA_API_HOST'])

    config['FIREWALL_SERVICE_NAME'] = "neutron server"
    config['FIREWALL_PORTS'] = "'9696'"
    config['FIREWALL_CHAIN'] = "INPUT"

    for host in q_hosts:
        manifest_file = "%s_neutron.pp" % (host,)
        manifest_data = getManifestTemplate("neutron.pp")
        manifest_data += getManifestTemplate(get_mq(config, "neutron"))
        appendManifestFile(manifest_file, manifest_data, 'neutron')

        if host in api_hosts:
            manifest_file = "%s_neutron.pp" % (host,)
            manifest_data = getManifestTemplate("neutron_api.pp")
            manifest_data += getManifestTemplate("neutron_notifications.pp")

            # Firewall Rules
            for f_host in allowed_hosts:
                config['FIREWALL_ALLOWED'] = "'%s'" % f_host
                config['FIREWALL_SERVICE_ID'] = "neutron_server_%s_%s" % (host, f_host)
                manifest_data += getManifestTemplate("firewall.pp")

            appendManifestFile(manifest_file, manifest_data, 'neutron')

        # Set up any l2 plugin configs we need anywhere we install neutron
        # XXX I am not completely sure about this, but it seems necessary:
        manifest_data = getManifestTemplate(plugin_manifest)
        appendManifestFile(manifest_file, manifest_data, 'neutron')


def create_keystone_manifest(config):
    manifestfile = "%s_keystone.pp" % config['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_neutron.pp")
    appendManifestFile(manifestfile, manifestdata)


def find_mapping(haystack, needle):
    return needle in [x.split(':')[1].strip() for x in get_values(haystack)]


def create_l3_manifests(config):
    global l3_hosts

    plugin = config['CONFIG_NEUTRON_L2_PLUGIN']
    if config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] == 'provider':
        config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = ''

    for host in l3_hosts:
        config['CONFIG_NEUTRON_L3_HOST'] = host
        config['CONFIG_NEUTRON_L3_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_l3.pp")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + '\n')
        if (config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch' and
                config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] and
                not find_mapping(config['CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'],
                                 config['CONFIG_NEUTRON_L3_EXT_BRIDGE'])):
            config['CONFIG_NEUTRON_OVS_BRIDGE'] = config['CONFIG_NEUTRON_L3_EXT_BRIDGE']
            manifestdata = getManifestTemplate('neutron_ovs_bridge.pp')
            appendManifestFile(manifestfile, manifestdata + '\n')


def create_dhcp_manifests(config):
    global dhcp_hosts

    plugin = config['CONFIG_NEUTRON_L2_PLUGIN']

    for host in dhcp_hosts:
        config["CONFIG_NEUTRON_DHCP_HOST"] = host
        config['CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'] = get_if_driver(config)
        manifest_data = getManifestTemplate("neutron_dhcp.pp")
        manifest_file = "%s_neutron.pp" % (host,)

        # Firewall Rules
        for f_host in q_hosts:
            config['FIREWALL_ALLOWED'] = "'%s'" % f_host
            config['FIREWALL_SERVICE_NAME'] = "neutron dhcp in"
            config['FIREWALL_SERVICE_ID'] = "neutron_dhcp_in_%s_%s" % (host, f_host)
            config['FIREWALL_PORTS'] = "'67'"
            config['FIREWALL_CHAIN'] = "INPUT"
            manifest_data += getManifestTemplate("firewall.pp")
            config['FIREWALL_SERVICE_NAME'] = "neutron dhcp out"
            config['FIREWALL_SERVICE_ID'] = "neutron_dhcp_out_%s_%s" % (host, f_host)
            config['FIREWALL_PORTS'] = "'68'"
            config['FIREWALL_CHAIN'] = "OUTPUT"
            manifest_data += getManifestTemplate("firewall.pp")

        appendManifestFile(manifest_file, manifest_data, 'neutron')



def create_lbaas_manifests(config):
    global lbaas_hosts
    for host in lbaas_hosts:
        controller.CONF['CONFIG_NEUTRON_LBAAS_INTERFACE_DRIVER'] = get_if_driver(config)
        manifestdata = getManifestTemplate("neutron_lbaas.pp")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")


def get_values(val):
    return [x.strip() for x in val.split(',')] if val else []

def get_agent_type(config):
    # The only real use case I can think of for multiples right now is to list
    # "vlan,gre" or "vlan,vxlan" so that VLANs are used if available,
    # but tunnels are used if not.
    tenant_types = config.get('CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES',
                              "['local']").strip('[]')
    tenant_types = [i.strip('"\'') for i in tenant_types.split(',')]

    for i in ['gre', 'vxlan', 'vlan']:
        if i in tenant_types:
            return i
    return tenant_types[0]

def create_l2_agent_manifests(config):
    global api_hosts, compute_hosts, dhcp_host, l3_hosts

    plugin = config['CONFIG_NEUTRON_L2_PLUGIN']
    agent = config["CONFIG_NEUTRON_L2_AGENT"]

    if agent == "openvswitch":
        host_var = 'CONFIG_NEUTRON_OVS_HOST'
        if plugin == agent:
            # monolithic plugin installation
            ovs_type = 'CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE'
            ovs_type = config.get(ovs_type, 'local')
        elif plugin == 'ml2':
            ovs_type = get_agent_type(config)
        else:
            raise RuntimeError('Invalid combination of plugin and agent.')
        template_name = "neutron_ovs_agent_%s.pp" % ovs_type

        bm_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"])
        iface_arr = get_values(config["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"])

        # The CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS parameter contains a
        # comma-separated list of bridge mappings. Since the puppet module
        # expects this parameter to be an array, this parameter must be properly
        # formatted by packstack, then consumed by the puppet module.
        # For example, the input string 'A, B, C' should formatted as '['A','B','C']'.
        config["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"] = str(bm_arr)
    elif agent == "linuxbridge":
        host_var = 'CONFIG_NEUTRON_LB_HOST'
        template_name = 'neutron_lb_agent.pp'
    else:
        raise KeyError("Unknown layer2 agent")

    # Install l2 agents on every compute host in addition to any hosts listed
    # specifically for the l2 agent
    for host in api_hosts | compute_hosts | dhcp_hosts | l3_hosts:
        config[host_var] = host
        manifestfile = "%s_neutron.pp" % (host,)
        manifestdata = getManifestTemplate(template_name)
        appendManifestFile(manifestfile, manifestdata + "\n")
        if agent == "openvswitch" and ovs_type == 'vlan':
            for if_map in iface_arr:
                config['CONFIG_NEUTRON_OVS_BRIDGE'], config['CONFIG_NEUTRON_OVS_IFACE'] = if_map.split(':')
                manifestdata = getManifestTemplate("neutron_ovs_port.pp")
                appendManifestFile(manifestfile, manifestdata + "\n")
        # Additional configurations required for compute hosts
        if host in compute_hosts:
            manifestdata = getManifestTemplate('neutron_bridge_module.pp')
            appendManifestFile(manifestfile, manifestdata + '\n')


def create_metadata_manifests(config):
    global meta_hosts
    if config.get('CONFIG_NOVA_INSTALL') == 'n':
        return
    for host in meta_hosts:
        controller.CONF['CONFIG_NEUTRON_METADATA_HOST'] = host
        manifestdata = getManifestTemplate('neutron_metadata.pp')
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")
