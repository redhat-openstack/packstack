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
Plugin responsible for setting OpenStack global options
"""

import distro
import glob
import logging
import os
import re
import uuid

from packstack.installer import basedefs
from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.common import filtered_hosts
from packstack.modules.common import is_all_in_one
from packstack.modules.documentation import update_params_usage

# ------------- Prescript Packstack Plugin Initialization --------------

PLUGIN_NAME = "Prescript"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    default_ssh_key = os.path.expanduser('~/.ssh/*.pub')
    default_ssh_key = (glob.glob(default_ssh_key) + [""])[0]
    params = {
        "GLOBAL": [
            {"CMD_OPTION": "ssh-public-key",
             "PROMPT": (
                 "Enter the path to your ssh Public key to install on servers"
             ),
             "OPTION_LIST": [],
             "VALIDATORS": [
                 validators.validate_file,
                 validators.validate_sshkey
             ],
             "PROCESSORS": [processors.process_ssh_key],
             "DEFAULT_VALUE": default_ssh_key,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SSH_KEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "default-password",
             "PROMPT": (
                 "Enter a default password to be used. Leave blank for a "
                 "randomly generated one."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_DEFAULT_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "service-workers",
             "PROMPT": (
                 "Enter the amount of service workers/threads to use for each "
                 "service. Leave blank to use the default."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '%{::processorcount}',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SERVICE_WORKERS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "mariadb-install",
             "PROMPT": "Should Packstack install MariaDB",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MARIADB_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_MYSQL_INSTALL']},

            {"CMD_OPTION": "os-glance-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Image Service (Glance)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_GLANCE_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-cinder-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Block Storage (Cinder)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-manila-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Shared File System "
                 "(Manila)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-nova-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Compute (Nova)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Networking (Neutron)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_neutron],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-horizon-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Dashboard (Horizon)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_HORIZON_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-swift-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Object Storage (Swift)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SWIFT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-ceilometer-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Metering (Ceilometer)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CEILOMETER_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-aodh-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Telemetry Alarming (Aodh)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_AODH_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-heat-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Orchestration (Heat)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "PROCESSORS": [processors.process_heat],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_HEAT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-magnum-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Container Infrastructure Management Service (Magnum)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MAGNUM_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-trove-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Database (Trove)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_TROVE_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-ironic-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Bare Metal (Ironic)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_IRONIC_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-client-install",
             "PROMPT": "Should Packstack install OpenStack client tools",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CLIENT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ntp-servers",
             "PROMPT": ("Enter a comma separated list of NTP server(s). Leave "
                        "plain if Packstack should not install ntpd "
                        "on instances."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NTP_SERVERS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "exclude-servers",
             "PROMPT": (
                 "Enter a comma separated list of server(s) to be excluded."
                 " Leave plain if you don't need to exclude any server."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "EXCLUDE_SERVERS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-debug-mode",
             "PROMPT": "Do you want to run OpenStack services in debug mode",
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_DEBUG_MODE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_CONTROLLER_HOST",
             "CMD_OPTION": "os-controller-host",
             "PROMPT": "Enter the controller host",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_CEILOMETER_HOST',
                            'CONFIG_CINDER_HOST',
                            'CONFIG_GLANCE_HOST',
                            'CONFIG_HORIZON_HOST',
                            'CONFIG_HEAT_HOST',
                            'CONFIG_IRONIC_HOST',
                            'CONFIG_KEYSTONE_HOST',
                            'CONFIG_NAGIOS_HOST',
                            'CONFIG_NEUTRON_SERVER_HOST',
                            'CONFIG_NOVA_API_HOST',
                            'CONFIG_NOVA_CERT_HOST',
                            'CONFIG_NOVA_VNCPROXY_HOST',
                            'CONFIG_NOVA_SCHED_HOST',
                            'CONFIG_OSCLIENT_HOST',
                            'CONFIG_SWIFT_PROXY_HOSTS']},

            {"CONF_NAME": "CONFIG_COMPUTE_HOSTS",
             "CMD_OPTION": "os-compute-hosts",
             "PROMPT": "Enter list of compute hosts",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_NOVA_COMPUTE_HOSTS']},

            {"CONF_NAME": "CONFIG_NETWORK_HOSTS",
             "CMD_OPTION": "os-network-hosts",
             "PROMPT": "Enter list of network hosts",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_NEUTRON_L3_HOSTS',
                            'CONFIG_NEUTRON_DHCP_HOSTS',
                            'CONFIG_NEUTRON_METADATA_HOSTS',
                            'CONFIG_NOVA_NETWORK_HOSTS']},

            {"CMD_OPTION": "os-vmware",
             "PROMPT": (
                 "Do you want to use VMware vCenter as hypervisor and "
                 "datastore"
             ),
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_VMWARE_BACKEND",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "unsupported",
             "PROMPT": (
                 "Enable this on your own risk. Do you want to use "
                 "unsupported parameters"
             ),
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_UNSUPPORTED",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "use-subnets",
             "PROMPT": ("Should interface names be automatically recognized "
                        "based on subnet CIDR"),
             "OPTION_LIST": ['y', 'n'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_USE_SUBNETS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "VMWARE": [
            {"CMD_OPTION": "vcenter-host",
             "PROMPT": (
                 "Enter the IP address of the VMware vCenter server to use "
                 "with Nova"
             ),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ip],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-username",
             "PROMPT": ("Enter the username to authenticate on VMware "
                        "vCenter server"),
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-password",
             "PROMPT": ("Enter the password to authenticate on VMware "
                        "vCenter server"),
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-clusters",
             "PROMPT": "Enter a comma separated list of vCenter datastores",
             "DEFAULT_VALUE": "",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_CLUSTER_NAMES",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_VCENTER_CLUSTER_NAME']},
        ],

        "UNSUPPORTED": [
            {"CONF_NAME": "CONFIG_STORAGE_HOST",
             "CMD_OPTION": "os-storage-host",
             "PROMPT": "Enter the host for the storage services",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "SERVERPREPARE": [
            {"CMD_OPTION": "additional-repo",
             "PROMPT": ("Enter a comma separated list of URLs to any "
                        "additional yum repositories to install"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_REPO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "enable-rdo-testing",
             "PROMPT": "To enable rdo testing enter \"y\"",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_ENABLE_RDO_TESTING",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "RHEL": [
            {"CMD_OPTION": "rh-username",
             "PROMPT": "To subscribe each server to Red Hat enter a username ",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_RH_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-server",
             "PROMPT": ("To subscribe each server with RHN Satellite enter "
                        "RHN Satellite server URL"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_URL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-sat6-server",
             "PROMPT": ("Specify a Satellite 6 Server to register to. If not"
                        " specified, Packstack will register the system to"
                        " the Red Hat server. When this option is specified,"
                        " you also need to set the Satellite 6 organization"
                        " and an activation key."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_SAT6_SERVER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "RHSM": [
            {"CMD_OPTION": "rh-password",
             "PROMPT": ("To subscribe each server to Red Hat enter your "
                        "password"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_RH_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-enable-optional",
             "PROMPT": "To enable RHEL optional repos use value \"y\"",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_RH_OPTIONAL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-proxy-host",
             "PROMPT": ("Specify a HTTP proxy to use with Red Hat subscription"
                        " manager"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_PROXY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-sat6-org",
             "PROMPT": ("Specify a Satellite 6 Server organization to use when"
                        " registering the system."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_SAT6_ORG",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-sat6-key",
             "PROMPT": ("Specify a Satellite 6 Server activation key to use"
                        " when registering the system."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_SAT6_KEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "RHSM_PROXY": [
            {"CMD_OPTION": "rh-proxy-port",
             "PROMPT": ("Specify port of Red Hat subscription manager HTTP "
                        "proxy"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_PROXY_PORT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-proxy-user",
             "PROMPT": ("Specify a username to use with Red Hat subscription "
                        "manager HTTP proxy"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_PROXY_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rh-proxy-password",
             "PROMPT": ("Specify a password to use with Red Hat subscription "
                        "manager HTTP proxy"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_RH_PROXY_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "SATELLITE": [
            {"CMD_OPTION": "rhn-satellite-username",
             "PROMPT": ("Enter RHN Satellite username or leave plain if you "
                        "will use activation key instead"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_SATELLITE_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-password",
             "PROMPT": ("Enter RHN Satellite password or leave plain if you "
                        "will use activation key instead"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-activation-key",
             "PROMPT": ("Enter RHN Satellite activation key or leave plain if "
                        "you used username/password instead"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_AKEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-cacert",
             "PROMPT": "Specify a path or URL to a SSL CA certificate to use",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_CACERT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-profile",
             "PROMPT": ("If required specify the profile name that should be "
                        "used as an identifier for the system "
                        "in RHN Satellite"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_PROFILE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-flags",
             "PROMPT": ("Enter comma separated list of flags passed "
                        "to rhnreg_ks"),
             "OPTION_LIST": ['novirtinfo', 'norhnsd', 'nopackages'],
             "VALIDATORS": [validators.validate_multi_options],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_FLAGS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-proxy-host",
             "PROMPT": "Specify a HTTP proxy to use with RHN Satellite",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_PROXY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "SATELLITE_PROXY": [
            {"CMD_OPTION": "rhn-satellite-proxy-username",
             "PROMPT": ("Specify a username to use with an authenticated "
                        "HTTP proxy"),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_PROXY_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "rhn-satellite-proxy-password",
             "PROMPT": ("Specify a password to use with an authenticated "
                        "HTTP proxy."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SATELLITE_PROXY_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, params)

    def use_vcenter(config):
        return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_VMWARE_BACKEND'] == 'y')

    def unsupported_enabled(config):
        return config['CONFIG_UNSUPPORTED'] == 'y'

    def filled_rhsm(config):
        return bool(config.get('CONFIG_RH_USER') or
                    config.get('CONFIG_RH_SAT6_SERVER'))

    def filled_rhsm_proxy(config):
        return bool(config.get('CONFIG_RH_PROXY'))

    def filled_satellite(config):
        return bool(config.get('CONFIG_SATELLITE_URL'))

    def filled_satellite_proxy(config):
        return bool(config.get('CONFIG_SATELLITE_PROXY'))

    groups = [
        {"GROUP_NAME": "GLOBAL",
         "DESCRIPTION": "Global Options",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "VMWARE",
         "DESCRIPTION": "vCenter Config Parameters",
         "PRE_CONDITION": use_vcenter,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "UNSUPPORTED",
         "DESCRIPTION": "Global unsupported options",
         "PRE_CONDITION": unsupported_enabled,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "SERVERPREPARE",
         "DESCRIPTION": "Server Prepare Configs ",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]

    config = controller.CONF
    if (is_all_in_one(config) and is_rhel()) or not is_all_in_one(config):
        groups.extend([
            {"GROUP_NAME": "RHEL",
             "DESCRIPTION": "RHEL config",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True},

            {"GROUP_NAME": "RHSM",
             "DESCRIPTION": "RH subscription manager config",
             "PRE_CONDITION": filled_rhsm,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True},

            {"GROUP_NAME": "RHSM_PROXY",
             "DESCRIPTION": "RH subscription manager proxy config",
             "PRE_CONDITION": filled_rhsm_proxy,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True},

            {"GROUP_NAME": "SATELLITE",
             "DESCRIPTION": "RHN Satellite config",
             "PRE_CONDITION": filled_satellite,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True},

            {"GROUP_NAME": "SATELLITE_PROXY",
             "DESCRIPTION": "RHN Satellite proxy config",
             "PRE_CONDITION": filled_satellite_proxy,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
        ])

    for group in groups:
        controller.addGroup(group, params[group['GROUP_NAME']])


def initSequences(controller):
    prescript_steps = [
        {'title': 'Discovering ip protocol version',
         'functions': [choose_ip_version]},
        {'title': 'Setting up ssh keys',
         'functions': [install_keys]},
        {'title': 'Preparing servers',
         'functions': [server_prep]},
        {'title': 'Pre installing Puppet and discovering hosts\' details',
         'functions': [preinstall_and_discover]},
        {'title': 'Preparing pre-install entries',
         'functions': [create_manifest]},
    ]

    if controller.CONF['CONFIG_NTP_SERVERS']:
        prescript_steps.append(
            {'title': 'Installing time synchronization via NTP',
             'functions': [create_ntp_manifest]})
    else:
        controller.MESSAGES.append('Time synchronization installation was '
                                   'skipped. Please note that unsynchronized '
                                   'time on server instances might be problem '
                                   'for some OpenStack components.')
    controller.addSequence("Running pre install scripts", [], [],
                           prescript_steps)

# ------------------------- helper functions -------------------------


def is_rhel():
    return 'Red Hat Enterprise Linux' in distro.linux_distribution()[0]


def detect_os_and_version(host):
    server = utils.ScriptRunner(host)
    server.append(
        'python -c "import distro; '
        'print distro.linux_distribution(full_distribution_name=0)[0]'
        '+\',\'+'
        'distro.linux_distribution()[1]"'
    )
    try:
        rc, out = server.execute()
        out = out.split(",")
        return out
    except exceptions.ScriptRuntimeError:
        logging.warning('Could not detect OS release')
        return ['Unknown', 'Unknown']


def run_rhn_reg(host, server_url, username=None, password=None,
                cacert=None, activation_key=None, profile_name=None,
                proxy_host=None, proxy_user=None, proxy_pass=None,
                flags=None):
    """
    Registers given host to given RHN Satellite server. To successfully
    register either activation_key or username/password is required.
    """
    logging.debug('Setting RHN Satellite server: %s.' % server_url)

    mask = []
    cmd = ['/usr/sbin/rhnreg_ks']
    server = utils.ScriptRunner(host)

    # check satellite server url
    server_url = (server_url.rstrip('/').endswith('/XMLRPC') and
                  server_url or '%s/XMLRPC' % server_url)
    cmd.extend(['--serverUrl', server_url])

    if activation_key:
        cmd.extend(['--activationkey', activation_key])
    elif username:
        cmd.extend(['--username', username])
        if password:
            cmd.extend(['--password', password])
            mask.append(password)
    else:
        raise exceptions.InstallError('Either RHN Satellite activation '
                                      'key or username/password must '
                                      'be provided.')

    if cacert:
        # use and if required download given certificate
        location = "/etc/sysconfig/rhn/%s" % os.path.basename(cacert)
        if not os.path.isfile(location):
            logging.debug('Downloading cacert from %s.' % server_url)
            wget_cmd = (f'ls {location} &> /dev/null && echo -n "" || '
                        'wget -nd --no-check-certificate --timeout=30 '
                        f'--tries=3 -O "{location}" "{cacert}"')
            server.append(wget_cmd)
        cmd.extend(['--sslCACert', location])

    if profile_name:
        cmd.extend(['--profilename', profile_name])
    if proxy_host:
        cmd.extend(['--proxy', proxy_host])
        if proxy_user:
            cmd.extend(['--proxyUser', proxy_user])
            if proxy_pass:
                cmd.extend(['--proxyPassword', proxy_pass])
                mask.append(proxy_pass)

    flags = flags or []
    flags.append('force')
    for i in flags:
        cmd.append('--%s' % i)

    server.append(' '.join(cmd))
    server.append('yum clean metadata')
    server.execute(mask_list=mask)


def run_rhsm_reg(host, username, password, optional=False, proxy_server=None,
                 proxy_port=None, proxy_user=None, proxy_password=None,
                 sat6_server=None, sat6_org=None, sat6_key=None):
    """
    Registers given host to Red Hat Repositories via subscription manager.
    """
    releasever = detect_os_and_version(host)[1].split('.')[0]
    server = utils.ScriptRunner(host)

    # configure proxy if it is necessary
    if proxy_server:
        cmd = ['subscription-manager', 'config',
               f'--server.proxy_hostname={proxy_server}',
               f'--server.proxy_port={proxy_port}']
        if proxy_user:
            cmd += [f'--server.proxy_user={proxy_user}',
                    f'--server.proxy_password={proxy_password}']
        server.append(cmd.join(' '))

    if sat6_server:
        # Register to Satellite 6 host
        cmd = ('curl -k -O'
               ' https://%s/pub/katello-ca-consumer-latest.noarch.rpm && '
               ' yum -y install katello-ca-consumer-latest.noarch.rpm &&'
               ' rm -f katello-ca-consumer-latest.noarch.rpm')
        server.append(cmd % sat6_server)
        cmd = ('subscription-manager register --org %s --activationkey %s')
        server.append(cmd % (sat6_org, sat6_key))
    else:
        # Register to Hosted RHSM
        cmd = ('subscription-manager register --username=\"%s\" '
               '--password=\"%s\" --autosubscribe || true')
        server.append(cmd % (username, password.replace('"', '\\"')))

        # subscribe to required channel
        cmd = ('subscription-manager list --consumed | grep -i openstack || '
               'subscription-manager subscribe --pool %s')
        pool = ("$(subscription-manager list --available | sed -n "
                "\'/Red Hat OpenStack/, /Pool ID:/"
                " { s/Pool ID:[[:space:]]*\\([[:alnum:]]*\\)/\\1/ p} \'"
                " | head -1 )")
        server.append(cmd % pool)

    if optional:
        server.append("subscription-manager repos "
                      "--enable rhel-%s-server-optional-rpms" % releasever)
        server.append("subscription-manager repos "
                      "--enable rhel-%s-server-extras-rpms" % releasever)
    server.append("subscription-manager repos "
                  "--enable rhel-%s-server-openstack-10-rpms" % releasever)

    server.append("yum clean all")
    server.append("rpm -q --whatprovides yum-utils || "
                  "yum install -y yum-utils")
    server.append("yum clean metadata")
    server.execute(mask_list=[password])


def manage_centos_release_openstack(host, config):
    """
    Installs and enables CentOS OpenStack release package if installed locally.
    """
    try:
        cmd = "rpm -qa --qf='%{name}-%{version}-%{release}.%{arch}\n' | grep centos-release-openstack"
        rc, out = utils.execute(cmd, use_shell=True)
    except exceptions.ExecuteRuntimeError:
        # No CentOS Cloud SIG repo, so we don't need to continue
        return

    match = re.match(r'^centos-release-openstack-(?P<branch>\w+)\-(?P<version>\w+)\-(?P<release>\d+\.[\d\w]+)', out)
    if not match:
        # No CentOS Cloud SIG repo, so we don't need to continue
        return
    branch = match.group('branch')

    server = utils.ScriptRunner(host)
    server.append(
        f"(rpm -q 'centos-release-openstack-{branch}' ||"
        f" yum -y install centos-release-openstack-{branch}) || true")

    try:
        server.execute()
    except exceptions.ScriptRuntimeError as ex:
        msg = ('Failed to set CentOS Cloud SIG repo on host %s:\n%s'
               % (host, ex))
        raise exceptions.ScriptRuntimeError(msg)


def manage_rdo(host, config):
    """
    Installs and enables RDO repo on host in case it is installed locally.
    """
    try:
        cmd = "rpm -q rdo-release --qf='%{version}-%{release}.%{arch}\n'"
        rc, out = utils.execute(cmd, use_shell=True)
    except exceptions.ExecuteRuntimeError:
        # RDO repo is not installed, so we don't need to continue
        return

    match = re.match(r'^(?P<version>\w+)\-.*\n', out)
    version = match.group('version')
    if re.match(r'^(.*\.el8.*\n)', out):
        dist_tag = '.el8'
    elif re.match(r'^(.*\.el9s.*\n)', out):
        dist_tag = '.el9s'
    else:
        dist_tag = ''
    rdo_url = (f"https://www.rdoproject.org/repos/openstack-{version}/"
               f"rdo-release-{version}{dist_tag}.rpm")

    server = utils.ScriptRunner(host)
    server.append(f"(rpm -q 'rdo-release-{version}' ||"
                  f" yum install -y --nogpg {rdo_url}) || true")
    try:
        server.execute()
    except exceptions.ScriptRuntimeError as ex:
        msg = 'Failed to set RDO repo on host %s:\n%s' % (host, ex)
        raise exceptions.ScriptRuntimeError(msg)

    reponame = 'openstack-%s' % version
    server.clear()
    server.append('yum-config-manager --enable %s' % reponame)

    if config['CONFIG_ENABLE_RDO_TESTING'] == 'y':
        server.append('yum-config-manager --disable %s' % reponame)
        server.append('yum-config-manager --enable %s-testing' % reponame)

    rc, out = server.execute()
    match = re.search(r'enabled\s*=\s*(1|True)', out)
    # In CentOS 7 yum-config-manager returns 0 always, but returns current setup
    # if succeeds
    # In CentOS 8 yum-config-manager returns 1 when failing but doesn't return current
    # setup if succeeds
    # In CentOS 9 yum-config-manager returns 1 when failing but doesn't return current
    # setup if succeeds
    if ((dist_tag == '.el9s' and rc != 0) or (dist_tag == '.el8' and rc != 0) or
            (dist_tag == '' and not match)):
        msg = ('Failed to set RDO repo on host %s:\nRPM file seems to be '
               'installed, but appropriate repo file is probably missing '
               'in /etc/yum.repos.d/' % host)
        raise exceptions.ScriptRuntimeError(msg)
# -------------------------- step functions --------------------------


def choose_ip_version(config, messages):
    use_ipv6 = None
    use_ipv4 = None
    for hostname in filtered_hosts(config):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        if use_ipv6 is None and use_ipv4 is None:
            use_ipv6 = utils.network.is_ipv6(hostname)
            use_ipv4 = utils.network.is_ipv4(hostname)
        # check consistency
        if (use_ipv6 and not utils.network.is_ipv6(hostname) or
                use_ipv4 and not utils.network.is_ipv4(hostname)):
            raise ValueError(
                "Inconsistent host format. Please use either IPv4 addresses, "
                "IPv6 adresses or hostnames for all host variables. "
            )
    if use_ipv6 and use_ipv4:
        msg = "IPv6 together with IPv4 installation is not supported"
        raise exceptions.ParamValidationError(msg)
    elif use_ipv6:
        config['CONFIG_IP_VERSION'] = 'ipv6'
    elif use_ipv4:
        config['CONFIG_IP_VERSION'] = 'ipv4'
    else:
        config['CONFIG_IP_VERSION'] = 'none'


def install_keys_on_host(hostname, sshkeydata):
    server = utils.ScriptRunner(hostname)
    # TODO(tbd) replace all that with ssh-copy-id
    server.append("mkdir -p ~/.ssh")
    server.append("chmod 500 ~/.ssh")
    server.append("grep '%s' ~/.ssh/authorized_keys > /dev/null 2>&1 || "
                  "echo %s >> ~/.ssh/authorized_keys"
                  % (sshkeydata, sshkeydata))
    server.append("chmod 400 ~/.ssh/authorized_keys")
    server.append("restorecon -r ~/.ssh")
    server.execute()


def install_keys(config, messages):
    with open(config["CONFIG_SSH_KEY"]) as fp:
        sshkeydata = fp.read().strip()

    # If this is a --allinone install *and* we are running as root,
    # we can configure the authorized_keys file locally, avoid problems
    # if PasswordAuthentication is disabled.
    if is_all_in_one(config) and os.getuid() == 0:
        install_keys_on_host(None, sshkeydata)
    else:
        for hostname in filtered_hosts(config):
            if '/' in hostname:
                hostname = hostname.split('/')[0]
            install_keys_on_host(hostname, sshkeydata)


def preinstall_and_discover(config, messages):
    """Installs Puppet and it's dependencies and dependencies of Puppet
    modules' package and discovers information about all hosts.
    """
    config['HOST_LIST'] = list(filtered_hosts(config))

    deps = list(basedefs.PUPPET_DEPENDENCIES) + list(basedefs.PUPPET_MODULES_DEPS)

    details = {}
    for hostname in config['HOST_LIST']:
        # install Puppet and it's dependencies
        server = utils.ScriptRunner(hostname)
        packages = ' '.join(deps)
        server.append('yum install -y %s' % packages)
        server.append('yum update -y %s' % packages)
        # yum does not fail if one of the packages is missing
        for package in deps:
            server.append('rpm -q --whatprovides %s' % package)
        server.execute()

        # create the packstack tmp directory
        server.clear()
        server.append('mkdir -p %s' % basedefs.PACKSTACK_VAR_DIR)
        # Separately create the tmp directory for this packstack run, this will
        # fail if the directory already exists
        host_dir = os.path.join(basedefs.PACKSTACK_VAR_DIR, uuid.uuid4().hex)
        server.append('mkdir --mode 0700 %s' % host_dir)
        for i in ('modules', 'resources'):
            server.append('mkdir --mode 0700 %s' % os.path.join(host_dir, i))
        server.execute()
        details.setdefault(hostname, {})['tmpdir'] = host_dir

        # discover other host info; Facter is installed as Puppet dependency,
        # so we let it do the work
        server.clear()
        server.append('facter -p')
        rc, stdout = server.execute()
        for line in stdout.split('\n'):
            try:
                key, value = line.split('=>', 1)
            except ValueError:
                # this line is probably some warning, so let's skip it
                continue
            else:
                details[hostname][key.strip()] = value.strip()

        # create a symbolic link to /etc/hiera.yaml to avoid warning messages
        # such as "Warning: Config file /etc/puppet/hiera.yaml not found,
        # using Hiera defaults"
        server.clear()
        server.append('[[ -f /etc/hiera.yaml ]] && '
                      '[[ ! -L /etc/puppet/hiera.yaml ]] && '
                      'ln -s /etc/hiera.yaml /etc/puppet/hiera.yaml || '
                      'echo "skipping creation of  hiera.yaml symlink"')
        server.append("sed -i 's;:datadir:.*;:datadir: "
                      "%s/hieradata;g' $(puppet config print hiera_config)"
                      % details[hostname]['tmpdir'])
        server.execute()
    config['HOST_DETAILS'] = details


def server_prep(config, messages):
    rh_username = None
    sat_url = None
    sat6_server = None
    if is_rhel():
        rh_username = config.get("CONFIG_RH_USER")
        rh_password = config.get("CONFIG_RH_PW")
        sat6_server = config.get("CONFIG_RH_SAT6_SERVER")

        sat_registered = set()

        sat_url = config["CONFIG_SATELLITE_URL"].strip()
        if sat_url:
            flag_list = config["CONFIG_SATELLITE_FLAGS"].split(',')
            sat_flags = [i.strip() for i in flag_list if i.strip()]
            sat_proxy_user = config.get("CONFIG_SATELLITE_PROXY_USER", '')
            sat_proxy_pass = config.get("CONFIG_SATELLITE_PROXY_PW", '')
            sat_args = {
                'username': config["CONFIG_SATELLITE_USER"].strip(),
                'password': config["CONFIG_SATELLITE_PW"].strip(),
                'cacert': config["CONFIG_SATELLITE_CACERT"].strip(),
                'activation_key': config["CONFIG_SATELLITE_AKEY"].strip(),
                'profile_name': config["CONFIG_SATELLITE_PROFILE"].strip(),
                'proxy_host': config["CONFIG_SATELLITE_PROXY"].strip(),
                'proxy_user': sat_proxy_user.strip(),
                'proxy_pass': sat_proxy_pass.strip(),
                'flags': sat_flags
            }

    for hostname in filtered_hosts(config):
        # Subscribe to Red Hat Repositories if configured
        if rh_username or sat6_server:
            run_rhsm_reg(hostname, rh_username, rh_password,
                         optional=(config.get('CONFIG_RH_OPTIONAL') == 'y'),
                         proxy_server=config.get('CONFIG_RH_PROXY'),
                         proxy_port=config.get('CONFIG_RH_PROXY_PORT'),
                         proxy_user=config.get('CONFIG_RH_PROXY_USER'),
                         proxy_password=config.get('CONFIG_RH_PROXY_PASSWORD'),
                         sat6_server=config.get('CONFIG_RH_SAT6_SERVER'),
                         sat6_org=config.get('CONFIG_RH_SAT6_ORG'),
                         sat6_key=config.get('CONFIG_RH_SAT6_KEY'))

        # Subscribe to RHN Satellite if configured
        if sat_url and hostname not in sat_registered:
            run_rhn_reg(hostname, sat_url, **sat_args)
            sat_registered.add(hostname)

        server = utils.ScriptRunner(hostname)
        server.append('rpm -q --whatprovides yum-utils || '
                      'yum install -y yum-utils')

        if is_rhel():
            # Installing rhos-log-collector if it is available from yum.
            server.append('yum list available rhos-log-collector && '
                          'yum -y install rhos-log-collector || '
                          'echo "no rhos-log-collector available"')

        server.execute()

        # enable CentOS Cloud SIG repo if installed locally
        manage_centos_release_openstack(hostname, config)
        # enable RDO if it is installed locally
        manage_rdo(hostname, config)

        # Add yum repositories if configured
        CONFIG_REPO = config["CONFIG_REPO"].strip()
        if CONFIG_REPO:
            for i, repourl in enumerate(CONFIG_REPO.split(',')):
                reponame = 'packstack_%d' % i
                server.append(f'echo "[{reponame}]\nname={reponame}\n'
                              f'baseurl={repourl}\nenabled=1\n'
                              'priority=1\ngpgcheck=0"'
                              f' > /etc/yum.repos.d/{reponame}.repo')

        server.append("yum clean metadata")
        server.execute()


def create_manifest(config, messages):
    key = 'CONFIG_DEBUG_MODE'
    config[key] = config[key] == 'y' and True or False

    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']
    if config['CONFIG_IP_VERSION'] == 'ipv6':
        storage_host = config['CONFIG_STORAGE_HOST']
        config['CONFIG_STORAGE_HOST_URL'] = "[%s]" % storage_host
    else:
        config['CONFIG_STORAGE_HOST_URL'] = config['CONFIG_STORAGE_HOST']


def create_ntp_manifest(config, messages):
    srvlist = [i.strip()
               for i in config['CONFIG_NTP_SERVERS'].split(',')
               if i.strip()]
    config['CONFIG_NTP_SERVERS'] = ' '.join(srvlist)

    definiton = '\n'.join(['server %s' % i for i in srvlist])
    config['CONFIG_NTP_SERVER_DEF'] = '%s\n' % definiton
