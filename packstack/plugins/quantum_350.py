"""
Installs and configures quantum
"""

import logging
import os
import uuid

from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-QUANTUM"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    logging.debug("Adding OpenStack Quantum configuration")

    conf_params = {
        "QUANTUM" : [
            {"CMD_OPTION"      : "quantum-server-host",
             "USAGE"           : "The IP addresses of the server on which to install the Quantum server",
             "PROMPT"          : "Enter the IP address of the Quantum server",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_ip, validators.validate_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_SERVER_HOST",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-use-namespaces",
             "USAGE"           : "Enable network namespaces for Quantum",
             "PROMPT"          : "Should Quantum use network namespaces?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "y",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_USE_NAMESPACES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-ks-password",
             "USAGE"           : "The password to use for Quantum to authenticate with Keystone",
             "PROMPT"          : "Enter the password for Quantum Keystone access",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_KS_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-db-password",
             "USAGE"           : "The password to use for Quantum to access DB",
             "PROMPT"          : "Enter the password for Quantum DB access",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_DB_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-l3-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Quantum L3 agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Quantum L3 agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_L3_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-l3-ext-bridge",
             "USAGE"           : "The name of the bridge that the Quantum L3 agent will use for external traffic",
             "PROMPT"          : "Enter the name of the bridge that the Quantum L3 agent will use for external traffic",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "br-ex",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_L3_EXT_BRIDGE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-dhcp-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Quantum DHCP plugin",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install Quantum DHCP plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_DHCP_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-l2-plugin",
             "USAGE"           : "The name of the L2 plugin to be used with Quantum",
             "PROMPT"          : "Enter the name of the L2 plugin to be used with Quantum",
             "OPTION_LIST"     : ["linuxbridge", "openvswitch"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "openvswitch",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_L2_PLUGIN",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-metadata-hosts",
             "USAGE"           : "A comma separated list of IP addresses on which to install Quantum metadata agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Quantum metadata agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_multi_ssh],
             "DEFAULT_VALUE"   : utils.get_localhost_ip(),
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_METADATA_HOSTS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-metadata-pw",
             "USAGE"           : "A comma separated list of IP addresses on which to install Quantum metadata agent",
             "PROMPT"          : "Enter a comma separated list of IP addresses on which to install the Quantum metadata agent",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
             "MASK_INPUT"      : True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_METADATA_PW",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : True,
             "CONDITION"       : False },
            ],
        "QUANTUM_LB_PLUGIN" : [
            {"CMD_OPTION"      : "quantum-lb-tenant-network-type",
             "USAGE"           : "The type of network to allocate for tenant networks",
             "PROMPT"          : "Enter the type of network to allocate for tenant networks",
             "OPTION_LIST"     : ["local", "vlan"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_LB_TENANT_NETWORK_TYPE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-lb-vlan-ranges",
             "USAGE"           : "A comma separated list of VLAN ranges for the Quantum linuxbridge plugin",
             "PROMPT"          : "Enter a comma separated list of VLAN ranges for the Quantum linuxbridge plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_LB_VLAN_RANGES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-lb-interface-mappings",
             "USAGE"           : "A comma separated list of interface mappings for the Quantum linuxbridge plugin",
             "PROMPT"          : "Enter a comma separated list of interface mappings for the Quantum linuxbridge plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_LB_INTERFACE_MAPPINGS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "QUANTUM_OVS_PLUGIN" : [
            {"CMD_OPTION"      : "quantum-ovs-tenant-network-type",
             "USAGE"           : "Type of network to allocate for tenant networks",
             "PROMPT"          : "Enter the type of network to allocate for tenant networks",
             "OPTION_LIST"     : ["local", "vlan", "gre"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "local",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME"       : "CONFIG_QUANTUM_OVS_TENANT_NETWORK_TYPE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-ovs-vlan-ranges",
             "USAGE"           : "A comma separated list of VLAN ranges for the Quantum openvswitch plugin",
             "PROMPT"          : "Enter a comma separated list of VLAN ranges for the Quantum openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_OVS_VLAN_RANGES",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "quantum-ovs-bridge-mappings",
             "USAGE"           : "A comma separated list of bridge mappings for the Quantum openvswitch plugin",
             "PROMPT"          : "Enter a comma separated list of bridge mappings for the Quantum openvswitch plugin",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [],
             "DEFAULT_VALUE"   : "physnet1:1000:2000",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_QUANTUM_OVS_BRIDGE_MAPPINGS",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        }

    def use_linuxbridge(config):
        return config['CONFIG_QUANTUM_INSTALL'] == 'y' and \
               config['CONFIG_QUANTUM_L2_PLUGIN'] == 'linuxbridge'

    def use_openvswitch(config):
        return config['CONFIG_QUANTUM_INSTALL'] == 'y' and \
               config['CONFIG_QUANTUM_L2_PLUGIN'] == 'openvswitch'

    conf_groups = [
        { "GROUP_NAME"            : "QUANTUM",
          "DESCRIPTION"           : "Quantum config",
          "PRE_CONDITION"         : "CONFIG_QUANTUM_INSTALL",
          "PRE_CONDITION_MATCH"   : "y",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "QUANTUM_LB_PLUGIN",
          "DESCRIPTION"           : "Quantum LB plugin config",
          "PRE_CONDITION"         : use_linuxbridge,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "QUANTUM_OVS_PLUGIN",
          "DESCRIPTION"           : "Quantum OVS plugin config",
          "PRE_CONDITION"         : use_openvswitch,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def getInterfaceDriver():
    if controller.CONF["CONFIG_QUANTUM_L2_PLUGIN"] == "openvswitch":
        return 'quantum.agent.linux.interface.OVSInterfaceDriver'
    elif controller.CONF['CONFIG_QUANTUM_L2_PLUGIN'] == 'linuxbridge':
        return 'quantum.agent.linux.interface.BridgeInterfaceDriver'


def initSequences(controller):
    if controller.CONF['CONFIG_QUANTUM_INSTALL'] != 'y':
        return
    if controller.CONF['CONFIG_QUANTUM_USE_NAMESPACES'] == 'y':
        controller.CONF['CONFIG_QUANTUM_USE_NAMESPACES'] = 'True'
    else:
        controller.CONF['CONFIG_QUANTUM_USE_NAMESPACES'] = 'False'

    global api_hosts, l3_hosts, dhcp_hosts, compute_hosts, meta_hosts, q_hosts
    api_hosts = set(controller.CONF['CONFIG_QUANTUM_SERVER_HOST'].split(','))
    l3_hosts = set(controller.CONF['CONFIG_QUANTUM_L3_HOSTS'].split(','))
    dhcp_hosts = set(controller.CONF['CONFIG_QUANTUM_DHCP_HOSTS'].split(','))
    meta_hosts = set(controller.CONF['CONFIG_QUANTUM_METADATA_HOSTS'].split(','))
    compute_hosts = set(controller.CONF['CONFIG_NOVA_COMPUTE_HOSTS'].split(','))
    q_hosts = api_hosts | l3_hosts | dhcp_hosts | compute_hosts | meta_hosts

    quantum_steps = [
        {'title': 'Adding Quantum API manifest entries', 'functions':[createManifest]},
        {'title': 'Adding Quantum Keystone manifest entries', 'functions':[createKeystoneManifest]},
        {'title': 'Adding Quantum L3 manifest entries', 'functions':[createL3Manifests]},
        {'title': 'Adding Quantum L2 Agent manifest entries', 'functions':[createL2AgentManifests]},
        {'title': 'Adding Quantum DHCP Agent manifest entries', 'functions':[createDHCPManifests]},
        {'title': 'Adding Quantum Metadata Agent manifest entries', 'functions':[createMetadataManifests]},
    ]
    controller.addSequence("Installing OpenStack Quantum", [], [], quantum_steps)


def createManifest(config):
    global q_hosts
    for host in q_hosts:
        if host in api_hosts:
            controller.CONF['CONFIG_QUANTUM_SERVER_ENABLE'] = 'true'
        else:
            controller.CONF['CONFIG_QUANTUM_SERVER_ENABLE'] = 'false'
        manifest_file = "%s_quantum.pp" % (host,)
        manifest_data = getManifestTemplate("quantum.pp")
        appendManifestFile(manifest_file, manifest_data, 'quantum')

        # Set up any l2 plugin configs we need anywhere we install quantum
        # XXX I am not completely sure about this, but it seems necessary
        if controller.CONF['CONFIG_QUANTUM_L2_PLUGIN'] == 'openvswitch':
            manifest_data = getManifestTemplate("quantum_ovs_plugin.pp")
            appendManifestFile(manifest_file, manifest_data, 'quantum')
        elif controller.CONF['CONFIG_QUANTUM_L2_PLUGIN'] == 'linuxbridge':
            # Eventually linuxbridge module will need to spearate plugin/agent functionality
            pass

def createKeystoneManifest(config):
    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_quantum.pp")
    appendManifestFile(manifestfile, manifestdata)

def createL3Manifests(config):
    global l3_hosts
    for host in l3_hosts:
        controller.CONF['CONFIG_QUANTUM_L3_HOST'] = host
        controller.CONF['CONFIG_QUANTUM_L3_INTERFACE_DRIVER'] = getInterfaceDriver()
        manifestdata = getManifestTemplate("quantum_l3.pp")
        manifestfile = "%s_quantum.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + '\n')
        if controller.CONF['CONFIG_QUANTUM_L2_PLUGIN'] == 'openvswitch' and controller.CONF['CONFIG_QUANTUM_L3_EXT_BRIDGE']:
            controller.CONF['CONFIG_QUANTUM_OVS_BRIDGE'] = controller.CONF['CONFIG_QUANTUM_L3_EXT_BRIDGE']
            manifestdata = getManifestTemplate('quantum_ovs_bridge.pp')
            appendManifestFile(manifestfile, manifestdata + '\n')

def createDHCPManifests(config):
    global dhcp_hosts
    for host in dhcp_hosts:
        controller.CONF["CONFIG_QUANTUM_DHCP_HOST"] = host
        controller.CONF['CONFIG_QUANTUM_DHCP_INTERFACE_DRIVER'] = getInterfaceDriver()
        manifestdata = getManifestTemplate("quantum_dhcp.pp")
        manifestfile = "%s_quantum.pp" % (host,)

        appendManifestFile(manifestfile, manifestdata + "\n")

def createL2AgentManifests(config):
    global compute_hosts, dhcp_host, l3_hosts

    if controller.CONF["CONFIG_QUANTUM_L2_PLUGIN"] == "openvswitch":
        host_var = 'CONFIG_QUANTUM_OVS_HOST'
        template_name = 'quantum_ovs_agent.pp'
    elif controller.CONF["CONFIG_QUANTUM_L2_PLUGIN"] == "linuxbridge":
        host_var = 'CONFIG_QUANTUM_LB_HOST'
        template_name = 'quantum_lb_agent.pp'
    else:
        raise KeyError("Unknown layer2 agent")

    # Install l2 agents on every compute host in addition to any hosts listed
    # specifically for the l2 agent
    for host in compute_hosts | dhcp_hosts | l3_hosts:
        controller.CONF[host_var] = host
        manifestdata = getManifestTemplate(template_name)
        manifestfile = "%s_quantum.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")

def createMetadataManifests(config):
    global meta_hosts

    for host in meta_hosts:
        controller.CONF['CONFIG_QUANTUM_METADATA_HOST'] = host
        manifestdata = getManifestTemplate('quantum_metadata.pp')
        manifestfile = "%s_quantum.pp" % (host,)
        appendManifestFile(manifestfile, manifestdata + "\n")
