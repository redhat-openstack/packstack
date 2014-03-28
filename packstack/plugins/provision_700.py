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

    def process_provision(param, process_args=None):
        return param if is_all_in_one(controller.CONF) else 'n'

    conf_params = {
        "PROVISION_INIT" : [
            {"CMD_OPTION"      : "provision-demo",
             "USAGE"           : ("Whether to provision for demo usage and testing. Note "
                                  "that provisioning is only supported for all-in-one "
                                  "installations."),
             "PROMPT"          : "Would you like to provision for demo usage and testing?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "PROCESSORS"      : [process_provision],
             "DEFAULT_VALUE"   : "y",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_DEMO",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "provision-tempest",
             "USAGE"           : ("Whether to configure tempest for testing. Note "
                                  "that provisioning is only supported for all-in-one "
                                  "installations."),
             "PROMPT"          : "Would you like to configure Tempest (OpenStack test suite)?",
             "OPTION_LIST"     : ["y", "n"],
             "VALIDATORS"      : [validators.validate_options],
             "PROCESSORS"      : [process_provision],
             "DEFAULT_VALUE"   : "n",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            ],
        "PROVISION_DEMO" : [
            {"CMD_OPTION"      : "provision-demo-floatrange",
             "USAGE"           : "The CIDR network address for the floating IP subnet",
             "PROMPT"          : "Enter the network address for the floating IP subnet:",
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
        "TEMPEST_GIT_REFS" : [
            {"CMD_OPTION"      : "provision-tempest-repo-uri",
             "USAGE"           : "The uri of the tempest git repository to use",
             "PROMPT"          : "What is the uri of the Tempest git repository?",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "https://github.com/openstack/tempest.git",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST_REPO_URI",
             "USE_DEFAULT"     : False,
             "NEED_CONFIRM"    : False,
             "CONDITION"       : False },
            {"CMD_OPTION"      : "provision-tempest-repo-revision",
             "USAGE"           : "The revision of the tempest git repository to use",
             "PROMPT"          : "What revision, branch, or tag of the Tempest git repository should be used?",
             "OPTION_LIST"     : [],
             "VALIDATORS"      : [validators.validate_not_empty],
             "DEFAULT_VALUE"   : "stable/havana",
             "MASK_INPUT"      : False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME"       : "CONFIG_PROVISION_TEMPEST_REPO_REVISION",
             "USE_DEFAULT"     : False,
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
        # resources are implemented).
        return is_all_in_one(config)

    def check_provisioning_demo(config):
        return (allow_provisioning(config) and
                (config.get('CONFIG_PROVISION_DEMO', 'n') == 'y' or
                 config.get('CONFIG_PROVISION_TEMPEST', 'n') == 'y'))

    def check_provisioning_tempest(config):
        return allow_provisioning(config) and \
               config.get('CONFIG_PROVISION_TEMPEST', 'n') == 'y'

    def allow_all_in_one_ovs_bridge(config):
        return allow_provisioning(config) and \
               config['CONFIG_NEUTRON_INSTALL'] == 'y' and \
               config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch'

    conf_groups = [
        { "GROUP_NAME"            : "PROVISION_INIT",
          "DESCRIPTION"           : "Provisioning demo config",
          "PRE_CONDITION"         : lambda x: 'yes',
          "PRE_CONDITION_MATCH"   : "yes",
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "PROVISION_DEMO",
          "DESCRIPTION"           : "Provisioning demo config",
          "PRE_CONDITION"         : check_provisioning_demo,
          "PRE_CONDITION_MATCH"   : True,
          "POST_CONDITION"        : False,
          "POST_CONDITION_MATCH"  : True },
        { "GROUP_NAME"            : "TEMPEST_GIT_REFS",
          "DESCRIPTION"           : "Optional tempest git uri and branch",
          "PRE_CONDITION"         : check_provisioning_tempest,
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

    # Due to group checking some parameters might not be initialized, but
    # provision.pp needs them all. So we will initialize them with default
    # values
    params = [
        controller.getParamByName(x)
        for x in ['CONFIG_PROVISION_TEMPEST_REPO_URI',
                  'CONFIG_PROVISION_TEMPEST_REPO_REVISION',
                  'CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE']
    ]
    for param in params:
        value = controller.CONF.get(param.CONF_NAME, param.DEFAULT_VALUE)
        controller.CONF[param.CONF_NAME] = value


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
    # Using the neutron or nova api servers as the provisioning target
    # will suffice for the all-in-one case.
    if config['CONFIG_NEUTRON_INSTALL'] == "y":
        host = config['CONFIG_NEUTRON_SERVER_HOST']
    else:
        host = config['CONFIG_NOVA_API_HOST']
        # The provisioning template requires the name of the external
        # bridge but the value will be missing if neutron isn't
        # configured to be installed.
        config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = 'br-ex'

    # Set template-specific parameter to configure whether neutron is
    # available.  The value needs to be true/false rather than the y/n.
    # provided by CONFIG_NEUTRON_INSTALL.
    config['PROVISION_NEUTRON_AVAILABLE'] = config['CONFIG_NEUTRON_INSTALL']
    marshall_conf_bool(config, 'PROVISION_NEUTRON_AVAILABLE')

    manifest_file = '%s_provision.pp' % host
    manifest_data = getManifestTemplate("provision.pp")
    appendManifestFile(manifest_file, manifest_data)
