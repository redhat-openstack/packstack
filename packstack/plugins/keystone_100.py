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
Installs and configures Keystone
"""

from packstack.installer import basedefs
from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.documentation import update_params_usage

# ------------- Keystone Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Keystone"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    keystone_params = {
        "KEYSTONE": [  # base keystone options
            {"CMD_OPTION": "keystone-db-passwd",
             "PROMPT": "Enter the password for the Keystone DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_password],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": 'keystone-fernet-token-rotate-enable',
             "PROMPT": (
                 "Enter y if cron job to rotate Fernet tokens should be "
                 "created"
             ),
             "OPTION_LIST": ['y', 'n'],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_bool],
             "DEFAULT_VALUE": 'y',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_FERNET_TOKEN_ROTATE_ENABLE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-region",
             "PROMPT": "Region name",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "RegionOne",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_REGION",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-admin-email",
             "PROMPT": "Enter the email address for the Keystone admin user",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "root@localhost",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_EMAIL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-admin-username",
             "PROMPT": "Enter the username for the Keystone admin user",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "admin",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_USERNAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-admin-passwd",
             "PROMPT": "Enter the password for the Keystone admin user",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-demo-passwd",
             "PROMPT": "Enter the password for the Keystone demo user",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_DEMO_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-api-version",
             "PROMPT": "Enter the Keystone API version string.",
             "OPTION_LIST": ['v3'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'v3',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_API_VERSION',
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-token-format",
             "PROMPT": "Enter the Keystone token format.",
             "OPTION_LIST": ['FERNET'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'FERNET',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_TOKEN_FORMAT',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-identity-backend",
             "PROMPT": "Enter the Keystone identity backend type.",
             "OPTION_LIST": ['sql', 'ldap'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "sql",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_IDENTITY_BACKEND',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ],

        "KEYSTONE_LDAP": [  # keystone ldap identity backend options
            {"CMD_OPTION": "keystone-ldap-url",
             "PROMPT": "Enter the Keystone LDAP backend URL.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ldap_url],
             "DEFAULT_VALUE": host_to_ldap_url(utils.get_localhost_ip()),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_URL',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-dn",
             "PROMPT": "Enter the Keystone LDAP user DN.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ldap_dn],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_DN',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-password",
             "PROMPT": "Enter the Keystone LDAP user password.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_PASSWORD',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-suffix",
             "PROMPT": "Enter the Keystone LDAP suffix.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty,
                            validators.validate_ldap_dn],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_SUFFIX',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-query-scope",
             "PROMPT": "Enter the Keystone LDAP query scope.",
             "OPTION_LIST": ['base', 'one', 'sub'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "one",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_QUERY_SCOPE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-page-size",
             "PROMPT": "Enter the Keystone LDAP query page size.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "-1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_PAGE_SIZE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-subtree",
             "PROMPT": "Enter the Keystone LDAP user subtree.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty,
                            validators.validate_ldap_dn],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_SUBTREE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-filter",
             "PROMPT": "Enter the Keystone LDAP user query filter.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_FILTER',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-objectclass",
             "PROMPT": "Enter the Keystone LDAP user objectclass.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_OBJECTCLASS',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-id-attribute",
             "PROMPT": "Enter the Keystone LDAP user ID attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ID_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-name-attribute",
             "PROMPT": "Enter the Keystone LDAP user name attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_NAME_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-mail-attribute",
             "PROMPT": "Enter the Keystone LDAP user email address attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_MAIL_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-enabled-attribute",
             "PROMPT": "Enter the Keystone LDAP user enabled attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ENABLED_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-enabled-mask",
             "PROMPT": "Enter the Keystone LDAP user enabled mask.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_integer],
             "DEFAULT_VALUE": "-1",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ENABLED_MASK',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-enabled-default",
             "PROMPT": "Enter the Keystone LDAP user enabled default.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "TRUE",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ENABLED_DEFAULT',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-enabled-invert",
             "PROMPT": "Enter the Keystone LDAP user enabled invert (n or y).",
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ENABLED_INVERT',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-attribute-ignore",
             "PROMPT": (
                 "Enter the comma separated Keystone LDAP user "
                 "attributes to ignore."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ATTRIBUTE_IGNORE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-default-project-id-attribute",
             "PROMPT": (
                 "Enter the Keystone LDAP user default_project_id attribute."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME":
             'CONFIG_KEYSTONE_LDAP_USER_DEFAULT_PROJECT_ID_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-pass-attribute",
             "PROMPT": "Enter the Keystone LDAP user password attribute.",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_PASS_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-enabled-emulation-dn",
             "PROMPT": "Enter the Keystone LDAP enabled emulation DN.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ldap_dn],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ENABLED_EMULATION_DN',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-additional-attribute-mapping",
             "PROMPT": (
                 "Enter the comma separated Keystone LDAP user additional "
                 "attribute mappings in the form "
                 "ldap_attr:user_attr[,ldap_attr:user_attr]...."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME":
             'CONFIG_KEYSTONE_LDAP_USER_ADDITIONAL_ATTRIBUTE_MAPPING',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-subtree",
             "PROMPT": "Enter the Keystone LDAP group subtree.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty,
                            validators.validate_ldap_dn],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_SUBTREE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-filter",
             "PROMPT": "Enter the Keystone LDAP group query filter.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_FILTER',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-objectclass",
             "PROMPT": "Enter the Keystone LDAP group objectclass.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_OBJECTCLASS',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-id-attribute",
             "PROMPT": "Enter the Keystone LDAP group ID attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_ID_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-name-attribute",
             "PROMPT": "Enter the Keystone LDAP group name attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_NAME_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-member-attribute",
             "PROMPT": "Enter the Keystone LDAP group member attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_MEMBER_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-desc-attribute",
             "PROMPT": "Enter the Keystone LDAP group description attribute.",
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_DESC_ATTRIBUTE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-attribute-ignore",
             "PROMPT": (
                 "Enter the comma separated Keystone LDAP group "
                 "attributes to ignore."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_ATTRIBUTE_IGNORE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-additional-attribute-mapping",
             "PROMPT": (
                 "Enter the comma separated Keystone LDAP group additional "
                 "attribute mappings in the form "
                 "ldap_attr:group_attr[,ldap_attr:group_attr]...."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME":
             'CONFIG_KEYSTONE_LDAP_GROUP_ADDITIONAL_ATTRIBUTE_MAPPING',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-use-tls",
             "PROMPT": (
                 "Enable TLS for Keystone communicating with "
                 "LDAP servers (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USE_TLS',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-tls-cacertdir",
             "PROMPT": "CA Certificate directory for Keystone LDAP.",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_TLS_CACERTDIR',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-tls-cacertfile",
             "PROMPT": "CA Certificate file for Keystone LDAP.",
             "OPTION_LIST": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_TLS_CACERTFILE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-tls-req-cert",
             "PROMPT": (
                 "Keystone LDAP certificate checking strictness "
                 "(never, allow, demand)"
             ),
             "OPTION_LIST": ["never", "allow", "demand"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "demand",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_TLS_REQ_CERT',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False}
        ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, keystone_params)
    keystone_groups = [
        {"GROUP_NAME": "KEYSTONE",
         "DESCRIPTION": "Keystone Config parameters",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "KEYSTONE_LDAP",
         "DESCRIPTION": "Keystone LDAP Identity Backend Config parameters",
         "PRE_CONDITION": 'CONFIG_KEYSTONE_IDENTITY_BACKEND',
         "PRE_CONDITION_MATCH": "ldap",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True}
    ]
    for group in keystone_groups:
        params = keystone_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    keystonesteps = [
        {'title':
         'Fixing Keystone LDAP config parameters to be undef if empty',
         'functions': [munge_ldap_config_params]},
        {'title': 'Preparing Keystone entries',
         'functions': [create_manifest]},
    ]
    controller.addSequence("Installing OpenStack Keystone", [], [],
                           keystonesteps)


# ------------------------- helper functions -------------------------

def host_to_ldap_url(hostfqdn):
    """Converts a host fqdn into an appropriate default
    LDAP URL.
    """
    return "ldap://%s" % hostfqdn


# -------------------------- step functions --------------------------

def munge_ldap_config_params(config, messages):
    def is_bool(keyname):
        return keyname in (
            'CONFIG_KEYSTONE_LDAP_USER_ENABLED_INVERT',
            'CONFIG_KEYSTONE_LDAP_USE_TLS'
        )

    def yn_to_bool(val):
        return {'n': False, 'y': True}.get(val, False)

    for key in config:
        if not key.startswith('CONFIG_KEYSTONE_LDAP_'):
            continue
        if key in ('CONFIG_KEYSTONE_LDAP_PAGE_SIZE',
                   'CONFIG_KEYSTONE_LDAP_USER_ENABLED_MASK'):
            if config[key] == '-1':
                config[key] = None
        elif is_bool(key):
            config[key] = yn_to_bool(config[key])
        elif config[key] == '':
            config[key] = None


def create_manifest(config, messages):
    if config['CONFIG_IP_VERSION'] == 'ipv6':
        host = config['CONFIG_CONTROLLER_HOST']
        config['CONFIG_KEYSTONE_HOST_URL'] = "[%s]" % host
    else:
        config['CONFIG_KEYSTONE_HOST_URL'] = config['CONFIG_CONTROLLER_HOST']

    config['CONFIG_KEYSTONE_PUBLIC_URL'] = "http://%s:5000/%s" % (
        config['CONFIG_KEYSTONE_HOST_URL'],
        config['CONFIG_KEYSTONE_API_VERSION']
    )
    config['CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'] = "http://%s:5000/" % (
        config['CONFIG_KEYSTONE_HOST_URL']
    )
    config['CONFIG_KEYSTONE_ADMIN_URL'] = "http://%s:5000" % (
        config['CONFIG_KEYSTONE_HOST_URL']
    )

    fw_details = dict()
    key = "keystone"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "keystone"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['5000']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_KEYSTONE_RULES'] = fw_details
