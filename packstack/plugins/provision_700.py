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
import json

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer.core import arch

from packstack.modules.documentation import update_params_usage

# ------------- Provision Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Provision"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

DEMO_IMAGE_NAME = 'cirros'
DEMO_IMAGE_URL = (
    'https://download.cirros-cloud.net/0.5.1/cirros-0.5.1-%s-disk.img'
    % (arch.cirros_arch())
)
DEMO_IMAGE_SSH_USER = 'cirros'
DEMO_IMAGE_FORMAT = 'qcow2'


def initConfig(controller):

    def process_tempest(param, param_name, config=None):
        if param == "":
            # In case of multinode installs by default we deploy
            # Tempest on network node
            return config['CONFIG_NETWORK_HOSTS'].split(',')[0]
        return param

    conf_params = {
        "PROVISION_INIT": [
            {"CMD_OPTION": "provision-demo",
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
             "PROMPT": "Enter the network address for the floating IP subnet",
             "OPTION_LIST": False,
             "VALIDATORS": False,
             "DEFAULT_VALUE": "172.24.4.0/24",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_DEMO_FLOATRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-demo-allocation-pools",
             "PROMPT": ("Enter the allocation pools from the floating IP "
                        "subnet, as JSON list [\"start=ip1,end=ip2\", ...]"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "[]",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_PROVISION_DEMO_ALLOCATION_POOLS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-image-name",
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

            {"CMD_OPTION": "provision-image-properties",
             "PROMPT": ("Enter the comma-separated list of key=value pairs "
                        "to set as the properties of the demo image"),
             "OPTION_LIST": False,
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_IMAGE_PROPERTIES",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-image-ssh-user",
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
            {"CMD_OPTION": "tempest-host",
             "PROMPT": "Enter the host where to deploy Tempest",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": "",
             "PROCESSORS": [process_tempest],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_TEMPEST_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-user",
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
             "PROMPT": "Enter the network address for the floating IP subnet",
             "OPTION_LIST": False,
             "VALIDATORS": False,
             "DEFAULT_VALUE": "172.24.4.0/24",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLOATRANGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-name",
             "PROMPT": "What is the name of the primary Tempest flavor?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "m1.nano",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-disk",
             "PROMPT": ("How much of disk space has "
                        "the primary Tempest flavor (Gb)?"),
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_DISK",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-ram",
             "PROMPT": "How much is the primary Tempest flavor's ram (Mb)?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "128",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_RAM",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-vcpus",
             "PROMPT": "How many vcpus is in the primary Tempest flavor?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_VCPUS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-alt-name",
             "PROMPT": "What is the name of the alternative Tempest flavor?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "m1.micro",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-alt-disk",
             "PROMPT": ("How much of disk space has "
                        "the alternative Tempest flavor (Gb)?"),
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_DISK",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-alt-ram",
             "PROMPT": "How much is the alternative Tempest flavor's ram?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "128",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_RAM",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "provision-tempest-flavor-alt-vcpus",
             "PROMPT": "How many vcpus has the alternative Tempest flavor?",
             "OPTION_LIST": False,
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_VCPUS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "run-tempest",
             "PROMPT": ("Do you wish to run tempest?"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_RUN_TEMPEST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "run-tempest-tests",
             "PROMPT": ("What tempest tests should run ?"
                        " (If blank, Tempest will run smoke tests)"),
             "OPTION_LIST": [],
             "VALIDATORS": False,
             "DEFAULT_VALUE": "smoke",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_RUN_TEMPEST_TESTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "skip-tempest-tests",
             "PROMPT": ("What tempest tests should skipped ?"
                        " (If blank, Tempest will not skip any tests)"),
             "OPTION_LIST": [],
             "VALIDATORS": False,
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_SKIP_TEMPEST_TESTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "PROVISION_OVS_BRIDGE": [
            {"CMD_OPTION": "provision-ovs-bridge",
             "PROMPT": "Would you like to configure the external ovs bridge",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_PROVISION_OVS_BRIDGE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE']},
        ],
    }
    update_params_usage(basedefs.PACKSTACK_DOC, conf_params)

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

        {"GROUP_NAME": "PROVISION_OVS_BRIDGE",
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
        controller.getParamByName('CONFIG_PROVISION_OVS_BRIDGE')
    ]
    for param in params:
        value = controller.CONF.get(param.CONF_NAME, param.DEFAULT_VALUE)
        controller.CONF[param.CONF_NAME] = value


def initSequences(controller):
    config = controller.CONF
    # params modification
    key = 'CONFIG_PROVISION_DEMO_ALLOCATION_POOLS'
    value = config.get(key, "[]")
    config[key] = json.loads(value)
    if type(config[key]) is not list:
        raise KeyError("Key %s is not a list: %s" % (key, config[key]))
