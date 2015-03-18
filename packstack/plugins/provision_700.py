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
Installs and configures Provisioning for demo usage and testing
"""

from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.common import is_all_in_one
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import getManifestTemplate

# ------------- Provision Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Provision"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

DEMO_IMAGE_NAME = 'cirros'
DEMO_IMAGE_URL = (
    'http://download.cirros-cloud.net/0.3.3/cirros-0.3.3-x86_64-disk.img'
)
DEMO_IMAGE_SSH_USER = 'cirros'
DEMO_IMAGE_FORMAT = 'qcow2'


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

            {"CMD_OPTION": "provision-image-name",
             "USAGE": "A named to be used for the demo image in Glance",
             "PROMPT": "Enter the name to be assigned to the demo image",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": DEMO_IMAGE_NAME,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_IMAGE_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-image-url",
             "USAGE": ("A URL or local file location for an image "
                       "to be loaded into Glance"),
             "PROMPT": ("Enter the location of an image to be loaded "
                        "into Glance"),
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": DEMO_IMAGE_URL,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_IMAGE_URL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-image-format",
             "USAGE": ("Disk format (qcow2, raw, etc) of demo image"),
             "PROMPT": ("Enter the format of the demo image"),
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": DEMO_IMAGE_FORMAT,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_IMAGE_FORMAT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-image-ssh-user",
             "USAGE": ("Name of a user to use when connecting via ssh to "
                       "instances booted from the demo image"),
             "PROMPT": ("Enter the name of a user to use when connecting "
                        "to the demo image via ssh"),
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": DEMO_IMAGE_SSH_USER,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_IMAGE_SSH_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "PROVISION_TEMPEST": [
            {"CMD_OPTION": "provision-tempest-user",
             "USAGE": "The name of the Tempest Provisioning user. If you "
                      "don't provide a user name, Tempest will be configured "
                      "in a standalone mode",
             "PROMPT": ("Enter the name of the Tempest Provisioning user "
                        "(if blank, Tempest will be configured in a "
                        "standalone mode) "),
             "OPTION_LIST": False,
             "VALIDATORS": False,
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-user-passwd",
             "USAGE": "The password to use for the Tempest Provisioning user",
             "PROMPT": "Enter the password for the Tempest Provisioning user",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_USER_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-floatrange",
             "USAGE": "The CIDR network address for the floating IP subnet",
             "PROMPT": "Enter the network address for the floating IP subnet",
             "OPTION_LIST": False,
             "VALIDATORS": False,
             "DEFAULT_VALUE": "172.24.4.224/28",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLOATRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

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
        return (config.get('CONFIG_PROVISION_DEMO', 'n') == 'y')

    def check_provisioning_tempest(config):
        return (config.get('CONFIG_PROVISION_TEMPEST', 'n') == 'y')

    def allow_all_in_one_ovs_bridge(config):
        return (config['CONFIG_NEUTRON_INSTALL'] == 'y')

    conf_groups = [
        {"GROUP_NAME": "PROVISION_INIT",
         "DESCRIPTION": "Provisioning demo config",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "PROVISION_DEMO",
         "DESCRIPTION": "Provisioning demo config",
         "PRE_CONDITION": check_provisioning_demo,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "PROVISION_TEMPEST",
         "DESCRIPTION": "Provisioning tempest config",
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

    if (config['CONFIG_PROVISION_DEMO'] != "y" and
            config['CONFIG_PROVISION_TEMPEST'] != "y"):
        return

    provision_steps = []

    if config['CONFIG_PROVISION_DEMO'] == "y":
        provision_steps.append(
            {'title': 'Adding Provisioning Demo manifest entries',
             'functions': [create_demo_manifest]}
        )

    if config['CONFIG_PROVISION_TEMPEST'] == "y":
        provision_steps.append(
            {'title': 'Adding Provisioning Tempest manifest entries',
             'functions': [create_tempest_manifest]}
        )
    provision_steps.append(
        {'title': 'Adding Provisioning Glance manifest entries',
         'functions': [create_storage_manifest]}
    )

    marshall_conf_bool(config, 'CONFIG_PROVISION_TEMPEST')
    marshall_conf_bool(config, 'CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE')

    controller.addSequence("Provisioning for Demo and Testing Usage",
                           [], [], provision_steps)


# ------------------------- helper functions -------------------------

def marshall_conf_bool(conf, key):
    if conf[key] == 'y':
        conf[key] = True
    else:
        conf[key] = False


def using_neutron(config):
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


# -------------------------- step functions --------------------------

def create_demo_manifest(config, messages):
    using_neutron(config)
    manifest_file = '%s_provision_demo.pp' % config['CONFIG_CONTROLLER_HOST']
    manifest_data = getManifestTemplate("provision_demo")
    appendManifestFile(manifest_file, manifest_data)


def create_storage_manifest(config, messages):
    if config['CONFIG_GLANCE_INSTALL'] == 'y':
        if config['CONFIG_UNSUPPORTED'] != 'y':
            config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

        if config['CONFIG_PROVISION_TEMPEST']:
            template = "provision_tempest_glance"
        else:
            template = "provision_demo_glance"
        manifest_file = '%s_provision_glance' % config['CONFIG_STORAGE_HOST']
        manifest_data = getManifestTemplate(template)
        appendManifestFile(manifest_file, manifest_data)


def create_tempest_manifest(config, messages):
    using_neutron(config)
    manifest_file = ('%s_provision_tempest.pp' %
                     config['CONFIG_CONTROLLER_HOST'])
    manifest_data = getManifestTemplate("provision_tempest")
    appendManifestFile(manifest_file, manifest_data)
