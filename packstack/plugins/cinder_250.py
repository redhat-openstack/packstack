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
Installs and configures Cinder
"""

import re

from packstack.installer import basedefs
from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.installer import utils

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------------ Cinder Packstack Plugin initialization ------------------

PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

NETAPP_DEFAULT_STORAGE_FAMILY = "ontap_cluster"
NETAPP_DEFAULT_STORAGE_PROTOCOL = "nfs"


def initConfig(controller):
    conf_params = {
        "CINDER": [
            {"CMD_OPTION": "cinder-db-passwd",
             "PROMPT": "Enter the password for the Cinder DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": 'cinder-db-purge-enable',
             "PROMPT": (
                 "Enter y if cron job for removing soft deleted DB rows "
                 "should be created"
             ),
             "OPTION_LIST": ['y', 'n'],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_bool],
             "DEFAULT_VALUE": 'y',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_CINDER_DB_PURGE_ENABLE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "cinder-ks-passwd",
             "PROMPT": "Enter the password for the Cinder Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "cinder-backend",
             "PROMPT": "Enter the Cinder backend to be configured",
             "OPTION_LIST": ["lvm", "nfs", "vmdk", "netapp",
                             "solidfire"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "lvm",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_BACKEND",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERVOLUMECREATE": [
            {"CMD_OPTION": "cinder-volumes-create",
             "PROMPT": ("Should Cinder's volumes group be created (for "
                        "proof-of-concept installation)?"),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_VOLUMES_CREATE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERVOLUMESIZE": [
            {"CMD_OPTION": "cinder-volumes-size",
             "PROMPT": "Enter Cinder's volumes group usable size",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "20G",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_VOLUMES_SIZE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERVOLUMENAME": [
            {"CMD_OPTION": "cinder-volume-name",
             "PROMPT": "Enter a name for the Cinder volume",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "cinder-volumes",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_VOLUME_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNFSMOUNTS": [
            {"CMD_OPTION": "cinder-nfs-mounts",
             "PROMPT": ("Enter a single or comma seprated list of NFS exports "
                        "to use with Cinder"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_multi_export],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NFS_MOUNTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPMAIN": [
            {"CMD_OPTION": "cinder-netapp-login",
             "PROMPT": ("Enter a NetApp login"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_LOGIN",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-password",
             "PROMPT": ("Enter a NetApp password"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-hostname",
             "PROMPT": ("Enter a NetApp hostname"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_add_quotes_around_values],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_HOSTNAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-server-port",
             "PROMPT": ("Enter a NetApp server port"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_port],
             "PROCESSORS": [],
             "DEFAULT_VALUE": 80,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_SERVER_PORT",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-storage-family",
             "PROMPT": ("Enter a NetApp storage family"),
             "OPTION_LIST": ["ontap_7mode", "ontap_cluster", "eseries"],
             "VALIDATORS": [validators.validate_options],
             "PROCESSORS": [],
             "DEFAULT_VALUE": NETAPP_DEFAULT_STORAGE_FAMILY,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_STORAGE_FAMILY",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-transport-type",
             "PROMPT": ("Enter a NetApp transport type"),
             "OPTION_LIST": ["http", "https"],
             "VALIDATORS": [validators.validate_options],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "http",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_TRANSPORT_TYPE",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-storage-protocol",
             "PROMPT": ("Enter a NetApp storage protocol"),
             "OPTION_LIST": ["iscsi", "fc", "nfs"],
             "VALIDATORS": [validators.validate_options],
             "PROCESSORS": [],
             "DEFAULT_VALUE": NETAPP_DEFAULT_STORAGE_PROTOCOL,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPONTAPISCSI": [
            {"CMD_OPTION": "cinder-netapp-size-multiplier",
             "PROMPT": ("Enter a NetApp size multiplier"),
             "OPTION_LIST": [""],
             "VALIDATORS": [],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "1.0",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPNFS": [
            {"CMD_OPTION": "cinder-netapp-expiry-thres-minutes",
             "PROMPT": ("Enter a threshold"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_integer],
             "PROCESSORS": [],
             "DEFAULT_VALUE": 720,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-thres-avl-size-perc-start",
             "PROMPT": ("Enter a value"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_integer],
             "PROCESSORS": [],
             "DEFAULT_VALUE": 20,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-thres-avl-size-perc-stop",
             "PROMPT": ("Enter a value"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_integer],
             "PROCESSORS": [],
             "DEFAULT_VALUE": 60,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-nfs-shares",
             "PROMPT": ("Enter a single or comma-separated list of NetApp NFS shares"),
             "OPTION_LIST": [""],
             "VALIDATORS": [],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_NFS_SHARES",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-nfs-shares-config",
             "PROMPT": ("Enter a NetApp NFS share config file"),
             "OPTION_LIST": [""],
             "VALIDATORS": [],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "/etc/cinder/shares.conf",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPISCSI7MODE": [
            {"CMD_OPTION": "cinder-netapp-volume-list",
             "PROMPT": ("Enter a NetApp volume list"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_VOLUME_LIST",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-vfiler",
             "PROMPT": ("Enter a NetApp vFiler"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_VFILER",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPP7MODEFC": [
            {"CMD_OPTION": "cinder-netapp-partner-backend-name",
             "PROMPT": ("Enter a NetApp partner backend name"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_PARTNER_BACKEND_NAME",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPVSERVER": [
            {"CMD_OPTION": "cinder-netapp-vserver",
             "PROMPT": ("Enter a NetApp Vserver"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_VSERVER",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPESERIES": [
            {"CMD_OPTION": "cinder-netapp-controller-ips",
             "PROMPT": ("Enter a value"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_multi_ping],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_CONTROLLER_IPS",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-sa-password",
             "PROMPT": ("Enter a password"),
             "OPTION_LIST": [""],
             "VALIDATORS": [],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_SA_PASSWORD",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-eseries-host-type",
             "PROMPT": ("Enter a host type"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "linux_dm_mp",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_ESERIES_HOST_TYPE",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-webservice-path",
             "PROMPT": ("Enter a path"),
             "OPTION_LIST": ["^[/].*$"],
             "VALIDATORS": [validators.validate_regexp],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "/devmgr/v2",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_WEBSERVICE_PATH",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-netapp-storage-pools",
             "PROMPT": ("Enter a value"),
             "OPTION_LIST": [""],
             "VALIDATORS": [],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_STORAGE_POOLS",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            ],

        "CINDERSOLIDFIRE": [
            {"CMD_OPTION": "cinder-solidfire-login",
             "PROMPT": ("Enter the cluster admin login"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_SOLIDFIRE_LOGIN",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-solidfire-password",
             "PROMPT": ("Enter cluster admin password"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_SOLIDFIRE_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
            {"CMD_OPTION": "cinder-solidfire-hostname",
             "PROMPT": ("Enter a SolidFire hostname or IP"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_add_quotes_around_values],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_SOLIDFIRE_HOSTNAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
            ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, conf_params)

    conf_groups = [
        {"GROUP_NAME": "CINDER",
         "DESCRIPTION": "Cinder Config parameters",
         "PRE_CONDITION": "CONFIG_CINDER_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERVOLUMECREATE",
         "DESCRIPTION": "Cinder volume create Config parameters",
         "PRE_CONDITION": check_lvm_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERVOLUMENAME",
         "DESCRIPTION": "Cinder volume custom name",
         "PRE_CONDITION": check_lvm_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERVOLUMESIZE",
         "DESCRIPTION": "Cinder volume size Config parameters",
         "PRE_CONDITION": check_lvm_vg_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNFSMOUNTS",
         "DESCRIPTION": "Cinder NFS Config parameters",
         "PRE_CONDITION": check_nfs_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPMAIN",
         "DESCRIPTION": "Cinder NetApp main configuration",
         "PRE_CONDITION": check_netapp_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPONTAPISCSI",
         "DESCRIPTION": "Cinder NetApp ONTAP-iSCSI configuration",
         "PRE_CONDITION": check_netapp_ontap_iscsi_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPNFS",
         "DESCRIPTION": "Cinder NetApp NFS configuration",
         "PRE_CONDITION": check_netapp_nfs_settings,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPISCSI7MODE",
         "DESCRIPTION": "Cinder NetApp iSCSI & 7-mode configuration",
         "PRE_CONDITION": check_netapp_7modeiscsi_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPP7MODEFC",
         "DESCRIPTION": "Cinder NetApp 7-mode Fibre Channel configuration",
         "PRE_CONDITION": check_netapp_7mode_fc_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPVSERVER",
         "DESCRIPTION": "Cinder NetApp Vserver configuration",
         "PRE_CONDITION": check_netapp_vserver_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPESERIES",
         "DESCRIPTION": "Cinder NetApp E-Series configuration",
         "PRE_CONDITION": check_netapp_eseries_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERSOLIDFIRE",
         "DESCRIPTION": "Cinder SolidFire configuration",
         "PRE_CONDITION": check_solidfire_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True}
        ]
    for group in conf_groups:
        params = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    config = controller.CONF
    if config['CONFIG_CINDER_INSTALL'] != 'y':
        return

    config['CONFIG_CINDER_BACKEND'] = (
        [i.strip() for i in config['CONFIG_CINDER_BACKEND'].split(',') if i]
    )

    for key in ('CONFIG_CINDER_NETAPP_VOLUME_LIST',
                'CONFIG_CINDER_NFS_MOUNTS'):
        if key in config:
            config[key] = [i.strip() for i in config[key].split(',') if i]

    cinder_steps = []

    if 'lvm' in config['CONFIG_CINDER_BACKEND']:
        cinder_steps.append(
            {'title': 'Checking if the Cinder server has a cinder-volumes vg',
             'functions': [check_cinder_vg]})

    cinder_steps.append(
        {'title': 'Preparing Cinder entries',
         'functions': [create_manifest]}
    )
    controller.addSequence("Installing OpenStack Cinder", [], [], cinder_steps)


# ------------------------- helper functions -------------------------

def check_lvm_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'lvm' in config['CONFIG_CINDER_BACKEND'])


def check_lvm_vg_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'lvm' in config['CONFIG_CINDER_BACKEND'])


def check_nfs_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'nfs' in config['CONFIG_CINDER_BACKEND'])


def check_netapp_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'netapp' in config['CONFIG_CINDER_BACKEND'])


def check_netapp_ontap_iscsi_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] in
            ['ontap_cluster', 'ontap_7mode'] and
            config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "iscsi")


def check_netapp_nfs_settings(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "nfs")


def check_netapp_7modeiscsi_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == 'ontap_7mode' and
            config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == 'iscsi')


def check_netapp_7mode_fc_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "ontap_7mode" and
            config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "fc")


def check_netapp_vserver_options(config):
    return (
        check_netapp_options(config) and
        config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "ontap_cluster" and
        config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] in ['nfs', 'iscsi'])


def check_netapp_eseries_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "eseries")


def check_solidfire_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'solidfire' in config['CONFIG_CINDER_BACKEND'])


# -------------------------- step functions --------------------------

def check_cinder_vg(config, messages):
    cinders_volume = config["CONFIG_CINDER_VOLUME_NAME"]

    # Do we have a cinder-volumes vg?
    have_cinders_volume = False
    server = utils.ScriptRunner(config['CONFIG_STORAGE_HOST'])
    server.append('vgdisplay %s' % cinders_volume)
    try:
        server.execute()
        have_cinders_volume = True
    except exceptions.ScriptRuntimeError:
        pass

    if config["CONFIG_CINDER_VOLUMES_CREATE"] == "n":
        if not have_cinders_volume:
            raise exceptions.MissingRequirements("The cinder server should "
                                                 "contain a volume group")
    match = re.match(r'^(?P<size>\d+)G$',
                     config['CONFIG_CINDER_VOLUMES_SIZE'].strip())
    if not match:
        msg = 'Invalid Cinder volumes VG size.'
        raise exceptions.ParamValidationError(msg)

    cinders_volume_size = int(match.group('size')) * 1024
    cinders_reserve = int(cinders_volume_size * 0.03)

    cinders_volume_size = cinders_volume_size + cinders_reserve
    config['CONFIG_CINDER_VOLUMES_SIZE'] = '%sM' % cinders_volume_size


def create_manifest(config, messages):
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        ssl_host = config['CONFIG_STORAGE_HOST']
        ssl_cert_file = config['CONFIG_CINDER_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_cinder.crt'
        )
        ssl_key_file = config['CONFIG_CINDER_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_cinder.key'
        )
        service = 'cinder'
        generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                          ssl_cert_file)

    fw_details = dict()
    for host in split_hosts(config['CONFIG_COMPUTE_HOSTS']):
        if (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_VMWARE_BACKEND'] == 'n'):
            key = "cinder_%s" % host
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "%s" % host
        else:
            key = "cinder_all"
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "ALL"

        fw_details[key]['service_name'] = "cinder"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['3260']
        fw_details[key]['proto'] = "tcp"

    config['FIREWALL_CINDER_RULES'] = fw_details

    # cinder API should be open for everyone
    fw_details = dict()
    key = "cinder_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "cinder-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8776']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_CINDER_API_RULES'] = fw_details
