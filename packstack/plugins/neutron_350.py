"""
Installs and configures neutron
"""

import logging
import os
import re
import uuid

from packstack.installer import utils
from packstack.installer import validators

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
            {"CMD_OPTION"      : "neutron-l2-plugin",
             "USAGE"           : "The name of the L2 plugin to be used with Neutron",
             "PROMPT"          : "Enter the name of the L2 plugin to be used with Neutron",
             "OPTION_LIST"     : ["linuxbridge", "openvswitch"],
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
             "USAGE"           : "The type of network to allocate for tenant networks",
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
             "USAGE"           : "A comma separated list of VLAN ranges for the Neutron linuxbridge plugin",
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
            {"CMD_OPTION"      : "neutron-lb-interface-mappings",
             "USAGE"           : "A comma separated list of interface mappings for the Neutron linuxbridge plugin",
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
             "USAGE"           : "Type of network to allocate for tenant networks",
             "PROMPT"          : "Enter the type of network to allocate for tenant networks",
             "OPTION_LIST"     : ["local", "vlan", "gre"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "neutron-ovs-vlan-ranges",
             "USAGE"           : "A comma separated list of VLAN ranges for the Neutron openvswitch plugin",
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
            {"CMD_OPTION"      : "neutron-ovs-bridge-mappings",
             "USAGE"           : "A comma separated list of bridge mappings for the Neutron openvswitch plugin",
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
        }

    def use_linuxbridge(config):
        return config['CONFIG_NEUTRON_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge'

    def use_openvswitch(config):
        return config['CONFIG_NEUTRON_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch'

    conf_groups = [
        { "GROUP_NAME"            : "NEUTRON",
          "DESCRIPTION"           : "Neutron config",
          "PRE_CONDITION"         : "CONFIG_NEUTRON_INSTALL",
          "PRE_CONDITION_MATCH"   : "y",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_LB_PLUGIN",
          "DESCRIPTION"           : "Neutron LB plugin config",
          "PRE_CONDITION"         : use_linuxbridge,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "NEUTRON_OVS_PLUGIN",
          "DESCRIPTION"           : "Neutron OVS plugin config",
          "PRE_CONDITION"         : use_openvswitch,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def getInterfaceDriver():
    if controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "openvswitch":
        return 'neutron.agent.linux.interface.OVSInterfaceDriver'
    elif controller.CONF['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge':
        return 'neutron.agent.linux.interface.BridgeInterfaceDriver'


def initSequences(controller):
    if controller.CONF['CONFIG_NEUTRON_INSTALL'] != 'y':
        return

    if controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "openvswitch":
        controller.CONF['CONFIG_NEUTRON_L2_DBNAME'] = 'ovs_neutron'
        controller.CONF['CONFIG_NEUTRON_CORE_PLUGIN'] = 'neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2'
    elif controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "linuxbridge":
        controller.CONF['CONFIG_NEUTRON_L2_DBNAME'] = 'neutron_linux_bridge'
        controller.CONF['CONFIG_NEUTRON_CORE_PLUGIN'] = 'neutron.plugins.linuxbridge.lb_neutron_plugin.LinuxBridgePluginV2'

    global api_hosts, l3_hosts, dhcp_hosts, compute_hosts, meta_hosts, q_hosts
    dirty = controller.CONF['CONFIG_NEUTRON_SERVER_HOST'].split(',')
    api_hosts = set([i.strip() for i in dirty if i.strip()])

    dirty = controller.CONF['CONFIG_NEUTRON_L3_HOSTS'].split(',')
    l3_hosts = set([i.strip() for i in dirty if i.strip()])

    dirty = controller.CONF['CONFIG_NEUTRON_DHCP_HOSTS'].split(',')
    dhcp_hosts = set([i.strip() for i in dirty if i.strip()])

    dirty = controller.CONF['CONFIG_NEUTRON_METADATA_HOSTS'].split(',')
    meta_hosts = set([i.strip() for i in dirty if i.strip()])

    dirty = controller.CONF['CONFIG_NOVA_COMPUTE_HOSTS'].split(',')
    compute_hosts = set([i.strip() for i in dirty if i.strip()])
    q_hosts = api_hosts | l3_hosts | dhcp_hosts | compute_hosts | meta_hosts

    neutron_steps = [
        {'title': 'Adding Neutron API manifest entries', 'functions':[createManifest]},
        {'title': 'Adding Neutron Keystone manifest entries', 'functions':[createKeystoneManifest]},
        {'title': 'Adding Neutron L3 manifest entries', 'functions':[createL3Manifests]},
        {'title': 'Adding Neutron L2 Agent manifest entries', 'functions':[createL2AgentManifests]},
        {'title': 'Adding Neutron DHCP Agent manifest entries', 'functions':[createDHCPManifests]},
        {'title': 'Adding Neutron Metadata Agent manifest entries', 'functions':[createMetadataManifests]},
    ]
    controller.addSequence("Installing OpenStack Neutron", [], [], neutron_steps)


def createManifest(config):
    global q_hosts

    for host in q_hosts:
        manifest_file = "%s_neutron.pp" % (host,)
        manifest_data = getManifestTemplate("neutron.pp")
        appendManifestFile(manifest_file, manifest_data, 'neutron')

        if host in api_hosts:
            manifest_file = "%s_neutron.pp" % (host,)
            manifest_data = getManifestTemplate("neutron_api.pp")
            appendManifestFile(manifest_file, manifest_data, 'neutron')

        # Set up any l2 plugin configs we need anywhere we install neutron
        # XXX I am not completely sure about this, but it seems necessary
        if controller.CONF['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch':
            manifest_data = getManifestTemplate("neutron_ovs_plugin.pp")
            appendManifestFile(manifest_file, manifest_data, 'neutron')
        elif controller.CONF['CONFIG_NEUTRON_L2_PLUGIN'] == 'linuxbridge':
            manifest_data = getManifestTemplate("neutron_lb_plugin.pp")
            appendManifestFile(manifest_file, manifest_data, 'neutron')

def createKeystoneManifest(config):
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_neutron.pp")
    appendManifestFile(manifestfile, manifestdata)

def createL3Manifests(config):
    global l3_hosts

    if controller.CONF['CONFIG_NEUTRON_L3_EXT_BRIDGE'] == 'provider':
        controller.CONF['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = ''

    for host in l3_hosts:
        controller.CONF['CONFIG_NEUTRON_L3_HOST'] = host
        controller.CONF['CONFIG_NEUTRON_L3_INTERFACE_DRIVER'] = getInterfaceDriver()
        manifestdata = getManifestTemplate("neutron_l3.pp")
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + '\n')
        if controller.CONF['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch' and controller.CONF['CONFIG_NEUTRON_L3_EXT_BRIDGE']:
            controller.CONF['CONFIG_NEUTRON_OVS_BRIDGE'] = controller.CONF['CONFIG_NEUTRON_L3_EXT_BRIDGE']
            manifestdata = getManifestTemplate('neutron_ovs_bridge.pp')
            appendManifestFile(manifestfile, manifestdata + '\n')

def createDHCPManifests(config):
    global dhcp_hosts
    for host in dhcp_hosts:
        controller.CONF["CONFIG_NEUTRON_DHCP_HOST"] = host
        controller.CONF['CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'] = getInterfaceDriver()
        manifestdata = getManifestTemplate("neutron_dhcp.pp")
        manifestfile = "%s_neutron.pp" % (host,)

        appendManifestFile(manifestfile, manifestdata + "\n")

def get_values(val):
    return [x.strip() for x in val.split(',')] if val else []

def createL2AgentManifests(config):
    global compute_hosts, dhcp_host, l3_hosts

    if controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "openvswitch":
        host_var = 'CONFIG_NEUTRON_OVS_HOST'
        template_name = 'neutron_ovs_agent.pp'

        bm_arr = get_values(controller.CONF["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"])
        iface_arr = get_values(controller.CONF["CONFIG_NEUTRON_OVS_BRIDGE_IFACES"])

        # The CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS parameter contains a
        # comma-separated list of bridge mappings. Since the puppet module
        # expects this parameter to be an array, this parameter must be properly
        # formatted by packstack, then consumed by the puppet module.
        # For example, the input string 'A, B, C' should formatted as '['A','B','C']'.
        controller.CONF["CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS"] = str(bm_arr)

    elif controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "linuxbridge":
        host_var = 'CONFIG_NEUTRON_LB_HOST'
        template_name = 'neutron_lb_agent.pp'
    else:
        raise KeyError("Unknown layer2 agent")

    # Install l2 agents on every compute host in addition to any hosts listed
    # specifically for the l2 agent
    for host in compute_hosts | dhcp_hosts | l3_hosts:
        controller.CONF[host_var] = host
        manifestfile = "%s_neutron.pp" % (host,)
        manifestdata = getManifestTemplate(template_name)
        appendManifestFile(manifestfile, manifestdata + "\n")
        if controller.CONF["CONFIG_NEUTRON_L2_PLUGIN"] == "openvswitch":
            for if_map in iface_arr:
                controller.CONF['CONFIG_NEUTRON_OVS_BRIDGE'], controller.CONF['CONFIG_NEUTRON_OVS_IFACE'] = if_map.split(':')
                manifestdata = getManifestTemplate("neutron_ovs_port.pp")
                appendManifestFile(manifestfile, manifestdata + "\n")

def createMetadataManifests(config):
    global meta_hosts

    for host in meta_hosts:
        controller.CONF['CONFIG_NEUTRON_METADATA_HOST'] = host
        manifestdata = getManifestTemplate('neutron_metadata.pp')
        manifestfile = "%s_neutron.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")
