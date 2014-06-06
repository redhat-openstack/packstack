# -*- coding: utf-8 -*-

"""
Installs and configures Cinder
"""

import os
import re
import uuid
import logging

from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.installer import basedefs
from packstack.installer import utils


from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)

from packstack.installer import exceptions
from packstack.installer import output_messages


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "cinder-db-passwd",
         "USAGE": "The password to use for the Cinder to access DB",
         "PROMPT": "Enter the password for the Cinder DB access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_DB_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "cinder-ks-passwd",
         "USAGE": ("The password to use for the Cinder to authenticate with "
                   "Keystone"),
         "PROMPT": "Enter the password for the Cinder Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_KS_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "cinder-backend",
         "USAGE": ("The Cinder backend to use, valid options are: lvm, "
                   "gluster, nfs, netapp"),
         "PROMPT": "Enter the Cinder backend to be configured",
         "OPTION_LIST": ["lvm", "gluster", "nfs", "netapp"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "lvm",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_BACKEND",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDER",
             "DESCRIPTION": "Cinder Config parameters",
             "PRE_CONDITION": "CONFIG_CINDER_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_lvm_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm')

    params = [
        {"CMD_OPTION": "cinder-volumes-create",
         "USAGE": ("Create Cinder's volumes group. This should only be done "
                   "for testing on a proof-of-concept installation of Cinder. "
                   "This will create a file-backed volume group and is not "
                   "suitable for production usage."),
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
    ]
    group = {"GROUP_NAME": "CINDERVOLUMECREATE",
             "DESCRIPTION": "Cinder volume create Config parameters",
             "PRE_CONDITION": check_lvm_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_lvm_vg_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm' and
                config.get('CONFIG_CINDER_VOLUMES_CREATE', 'y') == 'y')

    params = [
        {"CMD_OPTION": "cinder-volumes-size",
         "USAGE": ("Cinder's volumes group size. Note that actual volume size "
                   "will be extended with 3% more space for VG metadata."),
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
    ]
    group = {"GROUP_NAME": "CINDERVOLUMESIZE",
             "DESCRIPTION": "Cinder volume size Config parameters",
             "PRE_CONDITION": check_lvm_vg_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_gluster_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'gluster')

    params = [
        {"CMD_OPTION": "cinder-gluster-mounts",
         "USAGE": ("A single or comma separated list of gluster volume shares "
                   "to mount, eg: ip-address:/vol-name, domain:/vol-name "),
         "PROMPT": ("Enter a single or comma separated list of gluster volume "
                    "shares to use with Cinder"),
         "OPTION_LIST": ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'",
                         "^'[a-zA-Z0-9][\-\.\w]*:/.*'"],
         "VALIDATORS": [validators.validate_multi_regexp],
         "PROCESSORS": [processors.process_add_quotes_around_values],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_CINDER_GLUSTER_MOUNTS",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERGLUSTERMOUNTS",
             "DESCRIPTION": "Cinder gluster Config parameters",
             "PRE_CONDITION": check_gluster_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_nfs_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'nfs')

    params = [
        {"CMD_OPTION": "cinder-nfs-mounts",
         "USAGE": ("A single or comma seprated list of NFS exports to mount, "
                   "eg: ip-address:/export-name "),
         "PROMPT": ("Enter a single or comma seprated list of NFS exports to "
                    "use with Cinder"),
         "OPTION_LIST": ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'"],
         "VALIDATORS": [validators.validate_multi_regexp],
         "PROCESSORS": [processors.process_add_quotes_around_values],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_CINDER_NFS_MOUNTS",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERNFSMOUNTS",
             "DESCRIPTION": "Cinder NFS Config parameters",
             "PRE_CONDITION": check_nfs_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    # TODO - modify this code block to use NetApp specific settings
    def check_netapp_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'netapp')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-netapp-login",
                   "USAGE"           : ("(required) Administrative user account name used to access the storage "
                                        "system or proxy server. "),
                   "PROMPT"          : ("Enter a NetApp login"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_LOGIN",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-password",
                   "USAGE"           : ("(required) Password for the administrative user account specified in the"
                                        "netapp_login parameter."),
                   "PROMPT"          : ("Enter a NetApp password"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_PASSWORD",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-hostname",
                   "USAGE"           : ("(required) The hostname (or IP address) for the storage system or proxy"
                                        "server."),
                   "PROMPT"          : ("Enter a NetApp hostname"),
                   "OPTION_LIST"     : [], #"^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'"
                   "VALIDATORS"      : [], #
                   "PROCESSORS"      : [processors.process_add_quotes_around_values],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_HOSTNAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-server-port",
                   "USAGE"           : ("(optional) The TCP port to use for communication with ONTAPI on the"
                                        "storage system. Traditionally, port 80 is used for HTTP and port 443 is"
                                        "used for HTTPS; however, this value should be changed if an alternate"
                                        "port has been configured on the storage system or proxy server."
                                        "Defaults to 80"),
                   "PROMPT"          : ("Enter a NetApp server port"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_port],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : 80,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_SERVER_PORT",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-size-multiplier",
                   "USAGE"           : ("(optional) The quantity to be multiplied by the requested volume size to"
                                        "ensure enough space is available on the virtual storage server (Vserver) to"
                                        "fulfill the volume creation request."
                                        "Defaults to 1.2"),
                   "PROMPT"          : ("Enter a NetApp size multiplier"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_float],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "1.2",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-storage-family",
                   "USAGE"           : ("(optional) The storage family type used on the storage system; valid values"
                                        "are ontap_7mode for using Data ONTAP operating in 7-Mode or ontap_cluster"
                                        "for using clustered Data ONTAP, or eseries for NetApp E-Series."
                                        "Defaults to ontap_cluster"),
                   "PROMPT"          : ("Enter a NetApp storage family"),
                   "OPTION_LIST"     : ["ontap_7mode", "ontap_cluster"],
                   "VALIDATORS"      : [validators.validate_options],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "ontap_cluster",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_STORAGE_FAMILY",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-storage-protocol",
                   "USAGE"           : ("(optional) The storage protocol to be used on the data path with the storage"
                                        "system; valid values are iscsi or nfs."
                                        "Defaults to nfs"),
                   "PROMPT"          : ("Enter a NetApp storage protocol"),
                   "OPTION_LIST"     : ["iscsi", "nfs"],
                   "VALIDATORS"      : [validators.validate_options],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "nfs",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-transport-type",
                   "USAGE"           : ("(optional) The transport protocol used when communicating with ONTAPI on the"
                                        "storage system or proxy server. Valid values are http or https."
                                        "Defaults to http"),
                   "PROMPT"          : ("Enter a NetApp transport type"),
                   "OPTION_LIST"     : ["http", "https"],
                   "VALIDATORS"      : [validators.validate_options],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "http",  # default is not secure?
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_TRANSPORT_TYPE",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-vfiler",
                   "USAGE"           : ("(optional) The vFiler unit on which provisioning of block storage volumes"
                                        "will be done. This parameter is only used by the driver when connecting to"
                                        "an instance with a storage family of Data ONTAP operating in 7-Mode and the"
                                        "storage protocol selected is iSCSI. Only use this parameter when utilizing"
                                        "the MultiStore feature on the NetApp storage system."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a NetApp vFiler"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],  # would like to validate, but all validators test if it's empty and throw an errors
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_VFILER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-volume-list",
                   "USAGE"           : ("(optional) This parameter is only utilized when the storage protocol is"
                                        "configured to use iSCSI. This parameter is used to restrict provisioning to"
                                        "the specified controller volumes. Specify the value of this parameter to be"
                                        "a comma separated list of NetApp controller volume names to be used for"
                                        "provisioning."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a NetApp volume list"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_VOLUME_LIST",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-vserver",
                   "USAGE"           : ("(optional) This parameter specifies the virtual storage server (Vserver)"
                                        "name on the storage cluster on which provisioning of block storage volumes"
                                        "should occur. If using the NFS storage protocol, this parameter is mandatory"
                                        "for storage service catalog support (utilized by Cinder volume type"
                                        "extra_specs support). If this parameter is specified, the exports belonging"
                                        "to the Vserver will only be used for provisioning in the future. Block"
                                        "storage volumes on exports not belonging to the Vserver specified by"
                                        "this parameter will continue to function normally."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a NetApp Vserver"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_VSERVER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-expiry-thres-minutes",
                   "USAGE"           : ("(optional) This parameter specifies the threshold for last access time for"
                                        "images in the NFS image cache. When a cache cleaning cycle begins, images"
                                        "in the cache that have not been accessed in the last M minutes, where M is"
                                        "the value of this parameter, will be deleted from the cache to create free"
                                        "space on the NFS share."
                                        "Defaults to 720"),
                   "PROMPT"          : ("Enter a threshold"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_integer],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : 720,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_EXPIRY_THRES_MINUTES",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-thres-avl-size-perc-start",
                   "USAGE"           : ("(optional) If the percentage of available space for an NFS share has"
                                        "dropped below the value specified by this parameter, the NFS image cache"
                                        "will be cleaned."
                                        "Defaults to 20"),
                   "PROMPT"          : ("Enter a value"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_integer],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : 20,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_THRES_AVL_SIZE_PERC_START",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-thres-avl-size-perc-stop",
                   "USAGE"           : ("(optional) When the percentage of available space on an NFS share has reached the"
                                        "percentage specified by this parameter, the driver will stop clearing files"
                                        "from the NFS image cache that have not been accessed in the last M"
                                        "minutes, where M is the value of the expiry_thres_minutes parameter."
                                        "Defaults to 60"),
                   "PROMPT"          : ("Enter a value"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [validators.validate_integer],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : 60,
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_THRES_AVL_SIZE_PERC_STOP",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-nfs-shares-config",
                   "USAGE"           : ("(optional) File with the list of available NFS shares"
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a NFS share config file"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NFS_SHARES_CONFIG",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-copyoffload-tool-path",
                   "USAGE"           : ("(optional) This option specifies the path of the NetApp Copy Offload tool"
                                        "binary. Ensure that the binary has execute permissions set which allow the"
                                        "effective user of the cinder-volume process to execute the file."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a path"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_COPYOFFLOAD_TOOL_PATH",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-controller-ips",
                   "USAGE"           : ("(optional) This option is only utilized when the storage family is"
                                        "configured to eseries. This option is used to restrict provisioning to the"
                                        "specified controllers. Specify the value of this option to be a comma"
                                        "separated list of controller hostnames or IP addresses to be used for"
                                        "provisioning."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a value"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_CONTROLLER_IPS",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-sa-password",
                   "USAGE"           : ("(optional) Password for the NetApp E-Series storage array."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a password"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_SA_PASSWORD",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-storage-pools",
                   "USAGE"           : ("(optional) This option is used to restrict provisioning to the specified"
                                        "storage pools. Only dynamic disk pools are currently supported. Specify the"
                                        "value of this option to be a comma separated list of disk pool names to be"
                                        "used for provisioning."
                                        "Defaults to ''"),
                   "PROMPT"          : ("Enter a value"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_STORAGE_POOLS",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-netapp-webservice-path",
                   "USAGE"           : ("(optional) This option is used to specify the path to the E-Series proxy"
                                        "application on a proxy server. The value is combined with the value of the"
                                        "netapp_transport_type, netapp_server_hostname, and netapp_server_port"
                                        "options to create the URL used by the driver to connect to the proxy"
                                        "application."
                                        "Defaults to '/devmgr/v2'"),
                   "PROMPT"          : ("Enter a path"),
                   "OPTION_LIST"     : [""],
                   "VALIDATORS"      : [],
                   "PROCESSORS"      : [],
                   "DEFAULT_VALUE"   : "/devmgr/v2",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NETAPP_WEBSERVICE_PATH",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ]

    groupDict = { "GROUP_NAME"            : "CINDERNETAPPMOUNTS",
                  "DESCRIPTION"           : "Cinder NetApp Config parameters",
                  "PRE_CONDITION"         : check_netapp_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CINDER_INSTALL'] != 'y':
        return

    cinder_steps = [
        {'title': 'Installing dependencies for Cinder',
         'functions': [install_cinder_deps]},
        {'title': 'Adding Cinder Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Cinder manifest entries',
         'functions': [create_manifest]}
    ]

    if controller.CONF['CONFIG_CINDER_BACKEND'] == 'lvm':
        cinder_steps.append(
            {'title': 'Checking if the Cinder server has a cinder-volumes vg',
             'functions': [check_cinder_vg]})
    controller.addSequence("Installing OpenStack Cinder", [], [], cinder_steps)


#-------------------------- step functions --------------------------

def install_cinder_deps(config, messages):
    server = utils.ScriptRunner(config['CONFIG_CONTROLLER_HOST'])
    pkgs = []
    if config['CONFIG_CINDER_BACKEND'] == 'lvm':
        pkgs.append('lvm2')
    for p in pkgs:
        server.append("rpm -q --whatprovides %(package)s || "
                      "yum install -y %(package)s" % dict(package=p))
    server.execute()


def check_cinder_vg(config, messages):
    cinders_volume = 'cinder-volumes'

    # Do we have a cinder-volumes vg?
    have_cinders_volume = False
    server = utils.ScriptRunner(config['CONFIG_CONTROLLER_HOST'])
    server.append('vgdisplay %s' % cinders_volume)
    try:
        server.execute()
        have_cinders_volume = True
    except exceptions.ScriptRuntimeError:
        pass

    # Configure system LVM settings (snapshot_autoextend)
    server = utils.ScriptRunner(config['CONFIG_CONTROLLER_HOST'])
    server.append('sed -i -r "s/^ *snapshot_autoextend_threshold +=.*/'
                  '    snapshot_autoextend_threshold = 80/" '
                  '/etc/lvm/lvm.conf')
    server.append('sed -i -r "s/^ *snapshot_autoextend_percent +=.*/'
                  '    snapshot_autoextend_percent = 20/" '
                  '/etc/lvm/lvm.conf')
    try:
        server.execute()
    except exceptions.ScriptRuntimeError:
        logging.info("Warning: Unable to set system LVM settings.")

    if config["CONFIG_CINDER_VOLUMES_CREATE"] != "y":
        if not have_cinders_volume:
            raise exceptions.MissingRequirements("The cinder server should "
                                                 "contain a cinder-volumes "
                                                 "volume group")
    else:
        if have_cinders_volume:
            messages.append(
                output_messages.INFO_CINDER_VOLUMES_EXISTS)
            return

        server = utils.ScriptRunner(config['CONFIG_CONTROLLER_HOST'])
        server.append('systemctl')
        try:
            server.execute()
            rst_cmd = 'systemctl restart openstack-cinder-volume.service'
        except exceptions.ScriptRuntimeError:
            rst_cmd = 'service openstack-cinder-volume restart'

        server.clear()
        logging.info("A new cinder volumes group will be created")

        cinders_volume_path = '/var/lib/cinder'
        server.append('mkdir -p  %s' % cinders_volume_path)
        logging.debug("Volume's path: %s" % cinders_volume_path)

        match = re.match('^(?P<size>\d+)G$',
                         config['CONFIG_CINDER_VOLUMES_SIZE'].strip())
        if not match:
            msg = 'Invalid Cinder volumes VG size.'
            raise exceptions.ParamValidationError(msg)

        cinders_volume_size = int(match.group('size')) * 1024
        cinders_reserve = int(cinders_volume_size * 0.03)

        cinders_volume_size = cinders_volume_size + cinders_reserve
        cinders_volume_path = os.path.join(cinders_volume_path, cinders_volume)
        server.append('dd if=/dev/zero of=%s bs=1 count=0 seek=%sM'
                      % (cinders_volume_path, cinders_volume_size))
        server.append('LOFI=$(losetup --show -f  %s)' % cinders_volume_path)
        server.append('pvcreate $LOFI')
        server.append('vgcreate %s $LOFI' % cinders_volume)

        # Add the loop device on boot
        server.append('grep %(volume)s /etc/rc.d/rc.local || '
                      'echo "losetup -f %(path)s && '
                      'vgchange -a y %(volume)s && '
                      '%(restart_cmd)s" '
                      '>> /etc/rc.d/rc.local' %
                      {'volume': cinders_volume, 'restart_cmd': rst_cmd,
                       'path': cinders_volume_path})
        server.append('grep "#!" /etc/rc.d/rc.local || '
                      'sed -i \'1i#!/bin/sh\' /etc/rc.d/rc.local')
        server.append('chmod +x /etc/rc.d/rc.local')

        # Let's make sure it exists
        server.append('vgdisplay %s' % cinders_volume)

        try:
            server.execute()
        except exceptions.ScriptRuntimeError:
            # Release loop device if cinder's volume creation
            # fails.
            try:
                logging.debug("Release loop device, volume creation failed")
                server = utils.ScriptRunner(config['CONFIG_CONTROLLER_HOST'])
                server.append('losetup -d $(losetup -j %s | cut -d : -f 1)'
                              % cinders_volume_path)
                server.execute()
            except:
                pass

            raise exceptions.MissingRequirements("Cinder's volume group '%s' "
                                                 "could not be created"
                                                 % cinders_volume)


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    manifestdata = getManifestTemplate(get_mq(config, "cinder"))
    manifestfile = "%s_cinder.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata += getManifestTemplate("cinder.pp")

    if config['CONFIG_CINDER_BACKEND'] == "gluster":
        manifestdata += getManifestTemplate("cinder_gluster.pp")
    if config['CONFIG_CINDER_BACKEND'] == "nfs":
        manifestdata += getManifestTemplate("cinder_nfs.pp")
    if config['CONFIG_CINDER_BACKEND'] == "vmdk":
        manifestdata += getManifestTemplate("cinder_vmdk.pp")
    if config['CONFIG_CINDER_BACKEND'] == "netapp":
        manifestdata += getManifestTemplate("cinder_netapp.pp")
    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_ceilometer.pp')
    if config['CONFIG_SWIFT_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_backup.pp')

    config['FIREWALL_SERVICE_NAME'] = "cinder"
    config['FIREWALL_PORTS'] = "'3260', '8776'"
    config['FIREWALL_CHAIN'] = "INPUT"

    if (config['CONFIG_NOVA_INSTALL'] == 'y' and
            config['CONFIG_VMWARE_BACKEND'] == 'n'):
        for host in split_hosts(config['CONFIG_COMPUTE_HOSTS']):
            config['FIREWALL_ALLOWED'] = "'%s'" % host
            config['FIREWALL_SERVICE_ID'] = "cinder_%s" % host
            manifestdata += getManifestTemplate("firewall.pp")
    else:
        config['FIREWALL_ALLOWED'] = "'ALL'"
        config['FIREWALL_SERVICE_ID'] = "cinder_ALL"
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata)
