"""
Installs and configures neutron
"""

import logging

from packstack.installer import validators

from packstack.modules.common import is_all_in_one
from packstack.modules.ospluginutils import (appendManifestFile,
                                             getManifestTemplate)


# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Provision"

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject

    logging.debug("Provisioning OpenStack resources for demo usage and testing")

    conf_params = {
        "PROVISION_DEMO" : [
            {"CMD_OPTION"      : "provision-demo",
             "USAGE"           : "Whether to provision for demo usage and testing",
             "PROMPT"          : "Would you like to provision for demo usage and testing?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "n",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_DEMO",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "provision-demo-floatrange",
             "USAGE"           : "The CIDR network address for the floating IP subnet",
             "PROMPT"          : "Enter the network address for the floating IP subet:",
             "OPTION_LIST"     : False,
             "VALIDATORS"      : False,
             "DEFAULT_VALUE"   : "172.24.4.224/28",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_DEMO_FLOATRANGE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "PROVISION_TEMPEST" : [
            {"CMD_OPTION"      : "provision-tempest",
             "USAGE"           : "Whether to configure tempest for testing",
             "PROMPT"          : "Would you like to configure Tempest (OpenStack test suite)?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "n",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "provision-tempest-repo-uri",
             "USAGE"           : "The uri of the tempest git repository to use",
             "PROMPT"          : "What is the uri of the Tempest git repository?",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "https://github.com/redhat-openstack/tempest.git",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST_REPO_URI",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "provision-tempest-repo-revision",
             "USAGE"           : "The revision of the tempest git repository to use",
             "PROMPT"          : "What revision, branch, or tag of the Tempest git repository should be used?",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "master",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST_REPO_REVISION",
             "USE_DEFAULT"     : True,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "PROVISION_ALL_IN_ONE_OVS_BRIDGE" : [
            {"CMD_OPTION"      : "provision-all-in-one-ovs-bridge",
             "USAGE"           : "Whether to configure the ovs external bridge in an all-in-one deployment",
             "PROMPT"          : "Would you like to configure the external ovs bridge?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "DEFAULT_VALUE"   : "n",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        }

    def allow_provisioning(config):
        # Provisioning is currently supported only for all-in-one (due
        # to a limitation with how the custom types for OpenStack
        # resources are implemented) and neutron with namespaces (due
        # to the provisioning manifest assuming this configuration).
        return is_all_in_one(config) and \
               config['CONFIG_NEUTRON_INSTALL'] == 'y'

    def allow_all_in_one_ovs_bridge(config):
        return allow_provisioning(config) and \
               config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch'

    conf_groups = [
        { "GROUP_NAME"            : "PROVISION_DEMO",
          "DESCRIPTION"           : "Provisioning demo config",
          "PRE_CONDITION"         : allow_provisioning,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "PROVISION_TEMPEST",
          "DESCRIPTION"           : "Provisioning tempest config",
          "PRE_CONDITION"         : allow_provisioning,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "PROVISION_ALL_IN_ONE_OVS_BRIDGE",
          "DESCRIPTION"           : "Provisioning all-in-one ovs bridge config",
          "PRE_CONDITION"         : allow_all_in_one_ovs_bridge,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def marshall_conf_bool(conf, key):
    if conf[key] == 'y':
        conf[key] = 'true'
    else:
        conf[key] = 'false'


def initSequences(controller):
    provisioning_required = (
        controller.CONF['CONFIG_PROVISION_DEMO'] == 'y'
        or
        controller.CONF['CONFIG_PROVISION_TEMPEST'] == 'y'
    )
    if not provisioning_required:
        return
    marshall_conf_bool(controller.CONF, 'CONFIG_PROVISION_TEMPEST')
    marshall_conf_bool(controller.CONF,
                       'CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE')
    provision_steps = [
        {
            'title': 'Adding Provisioning manifest entries',
            'functions': [create_manifest],
        }
    ]
    controller.addSequence("Provisioning for Demo and Testing Usage",
                           [], [], provision_steps)


def create_manifest(config):
    # Using the server host will suffice for the all-in-one case.
    manifest_file = '%s_provision.pp' % (
        controller.CONF['CONFIG_NEUTRON_SERVER_HOST']
    )
    manifest_data = getManifestTemplate("provision.pp")
    appendManifestFile(manifest_file, manifest_data)
