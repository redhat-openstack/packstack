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
Installs and configures Nagios
"""

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.documentation import update_params_usage
from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import getManifestTemplate

# ------------- Nagios Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Nagios"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "nagios-passwd",
         "PROMPT": "Enter the password for the nagiosadmin user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_NAGIOS_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "NAGIOS",
             "DESCRIPTION": "Nagios Config parameters",
             "PRE_CONDITION": "CONFIG_NAGIOS_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_NAGIOS_INSTALL'] != 'y':
        return

    nagiossteps = [
        {'title': 'Adding Nagios server manifest entries',
         'functions': [create_manifest]},
        {'title': 'Adding Nagios host manifest entries',
         'functions': [create_nrpe_manifests]}
    ]
    controller.addSequence("Installing Nagios", [], [], nagiossteps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    config['CONFIG_NAGIOS_NODES'] = list(filtered_hosts(config))
    openstack_services = []
    openstack_services.append('keystone-user-list')

    if config['CONFIG_GLANCE_INSTALL'] == 'y':
        openstack_services.append('glance-index')

    if config['CONFIG_NOVA_INSTALL'] == 'y':
        openstack_services.append('nova-list')

    if config['CONFIG_CINDER_INSTALL'] == 'y':
        openstack_services.append('cinder-list')

    if config['CONFIG_SWIFT_INSTALL'] == 'y':
        openstack_services.append('swift-list')

    config['CONFIG_NAGIOS_SERVICES'] = openstack_services

    manifestfile = "%s_nagios.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("nagios_server")
    manifestdata += getManifestTemplate("apache_ports")
    appendManifestFile(manifestfile, manifestdata)


def create_nrpe_manifests(config, messages):
    for hostname in filtered_hosts(config):
        config['CONFIG_NRPE_HOST'] = hostname
        manifestfile = "%s_nagios_nrpe.pp" % hostname
        manifestdata = getManifestTemplate("nagios_nrpe")

        # Only the Nagios host is allowed to talk to nrpe
        fw_details = dict()
        key = "nagios_nrpe"
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % config['CONFIG_CONTROLLER_HOST']
        fw_details[key]['service_name'] = "nagios-nrpe"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['5666']
        fw_details[key]['proto'] = "tcp"
        config['FIREWALL_NAGIOS_NRPE_RULES'] = fw_details

        manifestdata += createFirewallResources('FIREWALL_NAGIOS_NRPE_RULES')
        appendManifestFile(manifestfile, manifestdata)

    messages.append("To use Nagios, browse to "
                    "http://%(CONFIG_CONTROLLER_HOST)s/nagios "
                    "username: nagiosadmin, password: %(CONFIG_NAGIOS_PW)s"
                    % config)
