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
Installs and configures Manila
"""

from packstack.installer import basedefs
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer import utils

from packstack.modules.documentation import update_params_usage
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import getManifestTemplate
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources

# ------------- Manila  Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Manila"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    conf_params = {
        "MANILA": [
            {"CMD_OPTION": "manila-db-passwd",
             "PROMPT": "Enter the password for the Manila DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "manila-ks-passwd",
             "PROMPT": "Enter the password for the Manila Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "manila-backend",
             "PROMPT": "Enter the Manila backend to be configured",
             "OPTION_LIST": ["generic", "netapp"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "generic",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_BACKEND",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "MANILANETAPP": [
            {"CMD_OPTION": "manila-netapp-nas-transport-type",
             "PROMPT": ("Enter a NetApp transport type"),
             "OPTION_LIST": ["http", "https"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "http",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_NAS_TRANSPORT_TYPE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-nas-login",
             "PROMPT": ("Enter a NetApp login"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "admin",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_NAS_LOGIN",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-nas-password",
             "PROMPT": ("Enter a NetApp password"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_NAS_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-nas-server-hostname",
             "PROMPT": ("Enter a NetApp hostname"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_add_quotes_around_values],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_NAS_SERVER_HOSTNAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-aggregate-name-search-pattern",
             "PROMPT": ("Enter a NetApp aggregate name search pattern"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "(.*)",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_AGGREGATE_NAME_SEARCH_PATTERN",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-root-volume-aggregate",
             "PROMPT": ("Enter a NetApp root volume aggregate"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_ROOT_VOLUME_AGGREGATE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-netapp-root-volume-name",
             "PROMPT": ("Enter a NetApp root volume name"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "root",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_NETAPP_ROOT_VOLUME_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "MANILAGENERIC": [
            {"CMD_OPTION": "manila-generic-volume-name-template",
             "PROMPT": ("Enter a volume name template"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "manila-share-%s",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_GENERIC_VOLUME_NAME_TEMPLATE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-generic-share-mount-path",
             "PROMPT": ("Enter a share mount path"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "/shares",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_GENERIC_SHARE_MOUNT_PATH",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-service-image-location",
             "PROMPT": ("Enter a service image location"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 'https://www.dropbox.com/s/vi5oeh10q1qkckh/'
                              'ubuntu_1204_nfs_cifs.qcow2',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_SERVICE_IMAGE_LOCATION",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-service-instance-user",
             "PROMPT": ("Enter a service instance user"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 'ubuntu',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_SERVICE_INSTANCE_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "manila-service-instance-password",
             "PROMPT": ("Enter a service instance password"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": 'ubuntu',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_SERVICE_INSTANCE_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, conf_params)
    conf_groups = [
        {"GROUP_NAME": "MANILA",
         "DESCRIPTION": "Manila Config parameters",
         "PRE_CONDITION": "CONFIG_MANILA_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "MANILANETAPP",
         "DESCRIPTION": "Manila NetApp configuration",
         "PRE_CONDITION": check_netapp_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "MANILAGENERIC",
         "DESCRIPTION": "Manila generic driver configuration",
         "PRE_CONDITION": check_generic_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in conf_groups:
        params = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_MANILA_INSTALL'] != 'y':
        return

    config['CONFIG_MANILA_BACKEND'] = (
        [i.strip() for i in config['CONFIG_MANILA_BACKEND'].split(',') if i]
    )

    manila_steps = [
        {'title': 'Adding Manila Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Manila manifest entries',
         'functions': [create_manifest]}
    ]

    controller.addSequence("Installing OpenStack Manila", [], [], manila_steps)


# ------------------------- helper functions -------------------------

def check_netapp_options(config):
    return (config.get('CONFIG_MANILA_INSTALL', 'n') == 'y' and
            config.get('CONFIG_MANILA_BACKEND', 'generic') == 'netapp')


def check_generic_options(config):
    return (config.get('CONFIG_MANILA_INSTALL', 'n') == 'y' and
            config.get('CONFIG_MANILA_BACKEND', 'generic') == 'generic')


# -------------------------- step functions --------------------------

def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_manila.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestdata = getManifestTemplate(get_mq(config, "manila"))
    manifestfile = "%s_manila.pp" % config['CONFIG_STORAGE_HOST']
    manifestdata += getManifestTemplate("manila.pp")

    backends = config['CONFIG_MANILA_BACKEND']
    for backend in backends:
        manifestdata += getManifestTemplate('manila_%s.pp' % backend)

    # manila API should be open for everyone
    fw_details = dict()
    key = "manila_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "manila-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8786']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_MANILA_API_RULES'] = fw_details
    manifestdata += createFirewallResources('FIREWALL_MANILA_API_RULES')

    appendManifestFile(manifestfile, manifestdata)
