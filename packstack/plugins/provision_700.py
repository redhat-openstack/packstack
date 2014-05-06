# -*- coding: utf-8 -*-

"""
Installs and configures neutron
"""

import logging

from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.common import is_all_in_one
from packstack.modules.ospluginutils import (appendManifestFile,
                                             getManifestTemplate)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Provision"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):

    def process_provision(param, process_args=None):
        return param if is_all_in_one(controller.CONF) else 'n'

    conf_params = {
        "PROVISION_INIT": [
            {"CMD_OPTION": "provision-demo",
             "USAGE": ("Whether to provision for demo usage and testing. Note "
                       "that provisioning is only supported for all-in-one "
                       "installations."),
             "PROMPT": ("Would you like to provision for demo usage "
                        "and testing"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_DEMO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest",
             "USAGE": "Whether to configure tempest for testing",
             "PROMPT": ("Would you like to configure Tempest (OpenStack test "
                        "suite). Note that provisioning is only supported for "
                        "all-in-one installations."),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            ],

        "PROVISION_DEMO": [
            {"CMD_OPTION": "provision-demo-floatrange",
             "USAGE": "The CIDR network address for the floating IP subnet",
             "PROMPT": "Enter the network address for the floating IP subnet",
             "OPTION_LIST": False,
             "VALIDATORS": False,
             "DEFAULT_VALUE": "172.24.4.224/28",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_DEMO_FLOATRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            ],

        "TEMPEST_GIT_REFS": [
            {"CMD_OPTION": "provision-tempest-repo-uri",
             "USAGE": "The uri of the tempest git repository to use",
             "PROMPT": "What is the uri of the Tempest git repository?",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "https://github.com/openstack/tempest.git",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_REPO_URI",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-repo-revision",
             "USAGE": "The revision of the tempest git repository to use",
             "PROMPT": ("What revision, branch, or tag of the Tempest git "
                        "repository should be used"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "master",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_REPO_REVISION",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "PROVISION_ALL_IN_ONE_OVS_BRIDGE": [
            {"CMD_OPTION": "provision-all-in-one-ovs-bridge",
             "USAGE": ("Whether to configure the ovs external bridge in an "
                       "all-in-one deployment"),
             "PROMPT": "Would you like to configure the external ovs bridge",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],
    }

    def check_provisioning_demo(config):
        return (allow_provisioning(config) and
                (config.get('CONFIG_PROVISION_DEMO', 'n') == 'y' or
                 config.get('CONFIG_PROVISION_TEMPEST', 'n') == 'y'))

    def check_provisioning_tempest(config):
        return (allow_provisioning(config) and
                config.get('CONFIG_PROVISION_TEMPEST', 'n') == 'y')

    def allow_all_in_one_ovs_bridge(config):
        return (allow_provisioning(config) and
                config['CONFIG_NEUTRON_INSTALL'] == 'y' and
                config['CONFIG_NEUTRON_L2_PLUGIN'] == 'openvswitch')

    conf_groups = [
        {"GROUP_NAME": "PROVISION_INIT",
         "DESCRIPTION": "Provisioning demo config",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "PROVISION_DEMO",
         "DESCRIPTION": "Provisioning demo config",
         "PRE_CONDITION": allow_provisioning,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "TEMPEST_GIT_REFS",
         "DESCRIPTION": "Optional tempest git uri and branch",
         "PRE_CONDITION": check_provisioning_tempest,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "PROVISION_ALL_IN_ONE_OVS_BRIDGE",
         "DESCRIPTION": "Provisioning all-in-one ovs bridge config",
         "PRE_CONDITION": allow_all_in_one_ovs_bridge,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
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


def initSequences(controller):
    config = controller.CONF
    provisioning_required = (
        config['CONFIG_PROVISION_DEMO'] == 'y'
        or
        config['CONFIG_PROVISION_TEMPEST'] == 'y'
    )

    if not provisioning_required or not allow_provisioning(config):
        return

    marshall_conf_bool(config, 'CONFIG_PROVISION_TEMPEST')
    marshall_conf_bool(config, 'CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE')

    provision_steps = [
        {'title': 'Adding Provisioning manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Provisioning for Demo and Testing Usage",
                           [], [], provision_steps)


#------------------------- helper functions -------------------------

def marshall_conf_bool(conf, key):
    if conf[key] == 'y':
        conf[key] = 'true'
    else:
        conf[key] = 'false'


def allow_provisioning(config):
    # Provisioning is currently supported only for all-in-one (due
    # to a limitation with how the custom types for OpenStack
    # resources are implemented).
    return is_all_in_one(config)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    # Using the neutron or nova api servers as the provisioning target
    # will suffice for the all-in-one case.
    if config['CONFIG_NEUTRON_INSTALL'] != "y":
        # The provisioning template requires the name of the external
        # bridge but the value will be missing if neutron isn't
        # configured to be installed.
        config['CONFIG_NEUTRON_L3_EXT_BRIDGE'] = 'br-ex'

    # Set template-specific parameter to configure whether neutron is
    # available.  The value needs to be true/false rather than the y/n.
    # provided by CONFIG_NEUTRON_INSTALL.
    config['PROVISION_NEUTRON_AVAILABLE'] = config['CONFIG_NEUTRON_INSTALL']
    marshall_conf_bool(config, 'PROVISION_NEUTRON_AVAILABLE')

    manifest_file = '%s_provision.pp' % config['CONFIG_CONTROLLER_HOST']
    manifest_data = getManifestTemplate("provision.pp")
    appendManifestFile(manifest_file, manifest_data)
