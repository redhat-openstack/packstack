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
Installs and configures Sahara
"""

from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import getManifestTemplate

# ------------------ Sahara installer initialization ------------------

PLUGIN_NAME = "OS-Sahara"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, "blue")


def initConfig(controller):
    params = [
        {"CONF_NAME": "CONFIG_SAHARA_DB_PW",
         "CMD_OPTION": "sahara-db-passwd",
         "PROMPT": "Enter the password to use for Sahara to access the DB",
         "USAGE": "The password to use for the Sahara DB access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_SAHARA_KS_PW",
         "CMD_OPTION": "sahara-ks-passwd",
         "USAGE": ("The password to use for Sahara to authenticate "
                   "with Keystone"),
         "PROMPT": "Enter the password for Sahara Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "SAHARA",
             "DESCRIPTION": "Sahara Config parameters",
             "PRE_CONDITION": "CONFIG_SAHARA_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    conf = controller.CONF
    if conf["CONFIG_SAHARA_INSTALL"] != 'y':
        return

    saharasteps = [
        {"title": "Adding Sahara Keystone manifest entries",
         "functions": [create_keystone_manifest]},
        {"title": "Adding Sahara manifest entries",
         "functions": [create_manifest]},
    ]
    controller.addSequence("Installing Sahara", [], [], saharasteps)

# -------------------------- step functions --------------------------


def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_SAHARA_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_sahara")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_sahara.pp" % config['CONFIG_STORAGE_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "sahara"))
    manifestdata += getManifestTemplate("sahara.pp")

    fw_details = dict()
    key = "sahara-api"
    fw_details.setdefault(key, {})
    fw_details[key]["host"] = "ALL"
    fw_details[key]["service_name"] = "sahara api"
    fw_details[key]["chain"] = "INPUT"
    fw_details[key]["ports"] = ["8386"]
    fw_details[key]["proto"] = "tcp"
    config["FIREWALL_SAHARA_CFN_RULES"] = fw_details

    manifestdata += createFirewallResources("FIREWALL_SAHARA_CFN_RULES")
    appendManifestFile(manifestfile, manifestdata, marker='sahara')
