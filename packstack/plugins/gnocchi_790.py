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
Installs and configures Gnocchi
"""

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators
from packstack.installer import processors

from packstack.modules.documentation import update_params_usage

# ------------- Gnocchi Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Gnocchi"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    gnocchi_params = {
        "GNOCCHI": [
            {"CONF_NAME": "CONFIG_GNOCCHI_DB_PW",
             "CMD_OPTION": "gnocchi-db-passwd",
             "PROMPT": "Enter the password for Gnocchi DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
            {"CONF_NAME": "CONFIG_GNOCCHI_KS_PW",
             "CMD_OPTION": "gnocchi-ks-passwd",
             "PROMPT": "Enter the password for the Gnocchi Keystone access",
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

    update_params_usage(basedefs.PACKSTACK_DOC, gnocchi_params)

    def use_gnocchi(config):
        return config['CONFIG_CEILOMETER_INSTALL'] == 'y'

    gnocchi_groups = [
        {"GROUP_NAME": "GNOCCHI",
         "DESCRIPTION": "Gnocchi Config parameters",
         "PRE_CONDITION": use_gnocchi,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in gnocchi_groups:
        paramList = gnocchi_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def initSequences(controller):
    if controller.CONF['CONFIG_CEILOMETER_INSTALL'] != 'y':
        return

    steps = [{'title': 'Preparing Gnocchi entries',
              'functions': [create_manifest]}]
    controller.addSequence("Installing OpenStack Gnocchi", [], [],
                           steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    fw_details = dict()
    key = "gnocchi_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "gnocchi-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8041']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_GNOCCHI_RULES'] = fw_details
