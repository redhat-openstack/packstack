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
Installs and configures Panko
"""

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage

# ------------- Panko Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Panko"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    panko_params = {
        "PANKO": [
            {"CONF_NAME": "CONFIG_PANKO_DB_PW",
             "CMD_OPTION": "panko-db-passwd",
             "PROMPT": "Enter the password for Panko DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
            {"CONF_NAME": "CONFIG_PANKO_KS_PW",
             "CMD_OPTION": "panko-ks-passwd",
             "PROMPT": "Enter the password for the Panko Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False}
        ]
    }

    update_params_usage(basedefs.PACKSTACK_DOC, panko_params)

    def use_panko(config):
        return (config['CONFIG_CEILOMETER_INSTALL'] == 'y' and
                config['CONFIG_PANKO_INSTALL'] == 'y')

    panko_groups = [
        {"GROUP_NAME": "PANKO",
         "DESCRIPTION": "Panko Config parameters",
         "PRE_CONDITION": use_panko,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in panko_groups:
        paramList = panko_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def initSequences(controller):
    if (controller.CONF['CONFIG_PANKO_INSTALL'] != 'y' or
       controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y'):
        return

    steps = [{'title': 'Preparing Panko entries',
              'functions': [create_manifest]}]
    controller.addSequence("Installing OpenStack Panko", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    fw_details = dict()
    key = "panko_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "panko-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8977']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_PANKO_RULES'] = fw_details
