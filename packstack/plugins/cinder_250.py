# -*- coding: utf-8 -*-

"""
Installs and configures Cinder
"""

import re

from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.installer import utils


from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


# ------------------ Cinder Packstack Plugin initialization ------------------

PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

NETAPP_DEFAULT_STORAGE_FAMILY = "ontap_cluster"
NETAPP_DEFAULT_STORAGE_PROTOCOL = "nfs"


def initConfig(controller):
    conf_params = {
        "CINDER": [
            {"CMD_OPTION": "cinder-db-passwd",
             "USAGE": "The password to use for the Cinder to access DB",
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

            {"CMD_OPTION": "cinder-ks-passwd",
             "USAGE": ("The password to use for the Cinder to authenticate "
                       "with Keystone"),
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
             "USAGE": ("The Cinder backend to use, valid options are: lvm, "
                       "gluster, nfs, netapp"),
             "PROMPT": "Enter the Cinder backend to be configured",
             "OPTION_LIST": ["lvm", "gluster", "nfs", "vmdk", "netapp"],
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
             "USAGE": ("Create Cinder's volumes group. This should only be "
                       "done for testing on a proof-of-concept installation "
                       "of Cinder. This will create a file-backed volume group"
                       " and is not suitable for production usage."),
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
             "USAGE": ("Cinder's volumes group size. Note that actual volume "
                       "size will be extended with 3% more space for VG "
                       "metadata."),
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

        "CINDERGLUSTERMOUNTS": [
            {"CMD_OPTION": "cinder-gluster-mounts",
             "USAGE": ("A single or comma separated list of gluster volume "
                       "shares to mount, eg: ip-address:/vol-name, "
                       "domain:/vol-name "),
             "PROMPT": ("Enter a single or comma separated list of gluster "
                        "volume shares to use with Cinder"),
             "OPTION_LIST": ["^([\d]{1,3}\.){3}[\d]{1,3}:/.*",
                             "^[a-zA-Z0-9][\-\.\w]*:/.*"],
             "VALIDATORS": [validators.validate_multi_regexp],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_CINDER_GLUSTER_MOUNTS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNFSMOUNTS": [
            {"CMD_OPTION": "cinder-nfs-mounts",
             "USAGE": ("A single or comma seprated list of NFS exports to "
                       "mount, eg: ip-address:/export-name "),
             "PROMPT": ("Enter a single or comma seprated list of NFS exports "
                        "to use with Cinder"),
             "OPTION_LIST": ["^([\d]{1,3}\.){3}[\d]{1,3}:/.*"],
             "VALIDATORS": [validators.validate_multi_regexp],
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
             "USAGE": ("(required) Administrative user account name used to "
                       "access the storage system or proxy server. "),
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
             "USAGE": ("(required) Password for the administrative user "
                       "account specified in the netapp_login parameter."),
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
             "USAGE": ("(required) The hostname (or IP address) for the "
                       "storage system or proxy server."),
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
             "USAGE": ("(optional) The TCP port to use for communication with "
                       "ONTAPI on the storage system. Traditionally, port 80 "
                       "is used for HTTP and port 443 is used for HTTPS; "
                       "however, this value should be changed if an alternate "
                       "port has been configured on the storage system or "
                       "proxy server.  Defaults to 80."),
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
             "USAGE": ("(optional) The storage family type used on the storage"
                       " system; valid values are ontap_7mode for using Data "
                       "ONTAP operating in 7-Mode or ontap_cluster for using "
                       "clustered Data ONTAP, or eseries for NetApp E-Series. "
                       "Defaults to %s." % NETAPP_DEFAULT_STORAGE_FAMILY),
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
             "USAGE": ("(optional) The transport protocol used when "
                       "communicating with ONTAPI on the storage system or "
                       "proxy server. Valid values are http or https.  "
                       "Defaults to http."),
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
             "USAGE": ("(optional) The storage protocol to be used on the data"
                       " path with the storage system; valid values are iscsi "
                       "or nfs. "
                       "Defaults to %s." % NETAPP_DEFAULT_STORAGE_PROTOCOL),
             "PROMPT": ("Enter a NetApp storage protocol"),
             "OPTION_LIST": ["iscsi", "nfs"],
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
             "USAGE": ("(optional) The quantity to be multiplied by the "
                       "requested volume size to ensure enough space is "
                       "available on the virtual storage server (Vserver)"
                       " to fulfill the volume creation request.  "
                       "Defaults to 1.0."),
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
             "USAGE": ("(optional) This parameter specifies the threshold for "
                       "last access time for images in the NFS image cache. "
                       "When a cache cleaning cycle begins, images in the "
                       "cache that have not been accessed in the last M "
                       "minutes, where M is the value of this parameter, will "
                       "be deleted from the cache to create free space on the "
                       "NFS share. Defaults to 720."),
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
             "USAGE": ("(optional) If the percentage of available space for an"
                       " NFS share has dropped below the value specified by "
                       "this parameter, the NFS image cache will be cleaned.  "
                       "Defaults to 20"),
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
             "USAGE": ("(optional) When the percentage of available space on "
                       "an NFS share has reached the percentage specified by "
                       "this parameter, the driver will stop clearing files "
                       "from the NFS image cache that have not been accessed "
                       "in the last M minutes, where M is the value of the "
                       "expiry_thres_minutes parameter.  "
                       "Defaults to 60."),
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
            {"CMD_OPTION": "cinder-netapp-nfs-shares-config",
             "USAGE": ("(optional) File with the list of available NFS shares."
                       "   Defaults to ''."),
             "PROMPT": ("Enter a NetApp NFS share config file"),
             "OPTION_LIST": [""],
             "VALIDATORS": [validators.validate_file],
             "PROCESSORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "CINDERNETAPPISCSI7MODE": [
            {"CMD_OPTION": "cinder-netapp-volume-list",
             "USAGE": ("(optional) This parameter is only utilized when the "
                       "storage protocol is configured to use iSCSI. This "
                       "parameter is used to restrict provisioning to the "
                       "specified controller volumes. Specify the value of "
                       "this parameter to be a comma separated list of NetApp "
                       "controller volume names to be used for provisioning.  "
                       "Defaults to ''."),
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
             "USAGE": ("(optional) The vFiler unit on which provisioning of "
                       "block storage volumes will be done. This parameter is "
                       "only used by the driver when connecting to an instance"
                       " with a storage family of Data ONTAP operating in "
                       "7-Mode and the storage protocol selected is iSCSI. "
                       "Only use this parameter when utilizing the MultiStore "
                       "feature on the NetApp storage system.  "
                       "Defaults to ''."),
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

        "CINDERNETAPPVSERVER": [
            {"CMD_OPTION": "cinder-netapp-vserver",
             "USAGE": ("(optional) This parameter specifies the virtual "
                       "storage server (Vserver) name on the storage cluster "
                       "on which provisioning of block storage volumes should "
                       "occur. If using the NFS storage protocol, this "
                       "parameter is mandatory for storage service catalog "
                       "support (utilized by Cinder volume type extra_specs "
                       "support). If this parameter is specified, the exports "
                       "belonging to the Vserver will only be used for "
                       "provisioning in the future. Block storage volumes on "
                       "exports not belonging to the Vserver specified by this"
                       "  parameter will "
                       "continue to function normally.  "
                       "Defaults to ''."),
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
             "USAGE": ("(optional) This option is only utilized when the "
                       "storage family is configured to eseries. This option "
                       "is used to restrict provisioning to the specified "
                       "controllers. Specify the value of this option to be a "
                       "comma separated list of controller hostnames or IP "
                       "addresses to be used for provisioning.  "
                       "Defaults to ''."),
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
             "USAGE": ("(optional) Password for the NetApp E-Series storage "
                       "array. "
                       "Defaults to ''."),
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
            {"CMD_OPTION": "cinder-netapp-webservice-path",
             "USAGE": ("(optional) This option is used to specify the path to "
                       "the E-Series proxy application on a proxy server. The "
                       "value is combined with the value of the "
                       "netapp_transport_type, netapp_server_hostname, and "
                       "netapp_server_port options to create the URL used by "
                       "the driver to connect to the proxy application.  "
                       "Defaults to '/devmgr/v2'."),
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
             "USAGE": ("(optional) This option is used to restrict "
                       "provisioning to the specified storage pools. Only "
                       "dynamic disk pools are currently supported. Specify "
                       "the value of this option to be a comma separated list "
                       "of disk pool names to be used for provisioning.  "
                       "Defaults to ''."),
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
            ]
    }

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

        {"GROUP_NAME": "CINDERVOLUMESIZE",
         "DESCRIPTION": "Cinder volume size Config parameters",
         "PRE_CONDITION": check_lvm_vg_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERGLUSTERMOUNTS",
         "DESCRIPTION": "Cinder gluster Config parameters",
         "PRE_CONDITION": check_gluster_options,
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

        {"GROUP_NAME": "CINDERNETAPPVSERVER",
         "DESCRIPTION": "Cinder NetApp vServer configuration",
         "PRE_CONDITION": check_netapp_vserver_options,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "CINDERNETAPPESERIES",
         "DESCRIPTION": "Cinder NetApp E-Series configuration",
         "PRE_CONDITION": check_netapp_eseries_options,
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
                'CONFIG_CINDER_GLUSTER_MOUNTS',
                'CONFIG_CINDER_NFS_MOUNTS'):
        if key in config:
            config[key] = [i.strip() for i in config[key].split(',') if i]

    cinder_steps = [
        {'title': 'Adding Cinder Keystone manifest entries',
         'functions': [create_keystone_manifest]}
    ]

    if 'lvm' in config['CONFIG_CINDER_BACKEND']:
        cinder_steps.append(
            {'title': 'Checking if the Cinder server has a cinder-volumes vg',
             'functions': [check_cinder_vg]})

    cinder_steps.append(
        {'title': 'Adding Cinder manifest entries',
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


def check_gluster_options(config):
    return (config['CONFIG_CINDER_INSTALL'] == 'y' and
            'gluster' in config['CONFIG_CINDER_BACKEND'])


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


def check_netapp_vserver_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "ontap_cluster"
            and config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] in
            ['nfs', 'iscsi'])


def check_netapp_eseries_options(config):
    return (check_netapp_options(config) and
            config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "eseries")


# -------------------------- step functions --------------------------

def check_cinder_vg(config, messages):
    cinders_volume = 'cinder-volumes'
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

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
                                                 "contain a cinder-volumes "
                                                 "volume group")
    match = re.match('^(?P<size>\d+)G$',
                     config['CONFIG_CINDER_VOLUMES_SIZE'].strip())
    if not match:
        msg = 'Invalid Cinder volumes VG size.'
        raise exceptions.ParamValidationError(msg)

    cinders_volume_size = int(match.group('size')) * 1024
    cinders_reserve = int(cinders_volume_size * 0.03)

    cinders_volume_size = cinders_volume_size + cinders_reserve
    config['CONFIG_CINDER_VOLUMES_SIZE'] = '%sM' % cinders_volume_size


def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestdata = getManifestTemplate(get_mq(config, "cinder"))
    manifestfile = "%s_cinder.pp" % config['CONFIG_STORAGE_HOST']
    manifestdata += getManifestTemplate("cinder.pp")

    backends = config['CONFIG_CINDER_BACKEND']
    if 'netapp' in backends:
        backends.remove('netapp')
        puppet_cdot_iscsi = "cinder_netapp_cdot_iscsi.pp"
        puppet_cdot_nfs = "cinder_netapp_cdot_nfs.pp"
        puppet_7mode_iscsi = "cinder_netapp_7mode_iscsi.pp"
        puppet_7mode_nfs = "cinder_netapp_7mode_nfs.pp"
        puppet_eseries = "cinder_netapp_eseries.pp"
        if config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "ontap_cluster":
            if config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "iscsi":
                manifestdata += getManifestTemplate(puppet_cdot_iscsi)
            elif config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "nfs":
                manifestdata += getManifestTemplate(puppet_cdot_nfs)
        elif config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "ontap_7mode":
            if config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "iscsi":
                manifestdata += getManifestTemplate(puppet_7mode_iscsi)
            elif config['CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'] == "nfs":
                manifestdata += getManifestTemplate(puppet_7mode_nfs)
        elif config['CONFIG_CINDER_NETAPP_STORAGE_FAMILY'] == "eseries":
            manifestdata += getManifestTemplate(puppet_eseries)
    for backend in backends:
        manifestdata += getManifestTemplate('cinder_%s.pp' % backend)

    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_ceilometer.pp')
    if config['CONFIG_SWIFT_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_backup.pp')

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
    manifestdata += createFirewallResources('FIREWALL_CINDER_RULES')

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
    manifestdata += createFirewallResources('FIREWALL_CINDER_API_RULES')

    appendManifestFile(manifestfile, manifestdata)
