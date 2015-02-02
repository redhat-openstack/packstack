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

import uuid

from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import createFirewallResources
from packstack.modules.ospluginutils import getManifestTemplate

# ------------- Keystone Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Keystone"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    keystone_params = {
        "KEYSTONE": [  # base keystone options
            {"CMD_OPTION": "keystone-db-passwd",
             "USAGE": "The password to use for the Keystone to access DB",
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

            {"CMD_OPTION": "keystone-region",
             "USAGE": "Region name",
             "PROMPT": "Region name",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "RegionOne",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_REGION",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-admin-token",
             "USAGE": "The token to use for the Keystone service api",
             "PROMPT": "The token to use for the Keystone service api",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": uuid.uuid4().hex,
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_KEYSTONE_ADMIN_TOKEN",
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-admin-passwd",
             "USAGE": "The password to use for the Keystone admin user",
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
             "USAGE": "The password to use for the Keystone demo user",
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

            {"CMD_OPTION": "keystone-token-format",
             "USAGE": "Keystone token format. Use either UUID or PKI",
             "PROMPT": "Enter the Keystone token format.",
             "OPTION_LIST": ['UUID', 'PKI'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'UUID',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_TOKEN_FORMAT',
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-service-name",
             "USAGE": (
                 "Name of service to use to run keystone (keystone or httpd)"
             ),
             "PROMPT": "Enter the Keystone service name.",
             "OPTION_LIST": ['keystone', 'httpd'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "httpd",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_SERVICE_NAME',
             "USE_DEFAULT": True,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-identity-backend",
             "USAGE": "Type of identity backend (sql or ldap)",
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
             "USAGE": "Keystone LDAP backend URL",
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
             "USAGE": (
                 "Keystone LDAP backend user DN.  Used to bind to the LDAP "
                 "server when the LDAP server does not allow anonymous "
                 "authentication."
             ),
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
             "USAGE": "Keystone LDAP backend password for user DN",
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
             "USAGE": "Keystone LDAP backend base suffix",
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
             "USAGE": "Keystone LDAP backend query scope (base, one, sub)",
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
             "USAGE": "Keystone LDAP backend query page size",
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
             "USAGE": "Keystone LDAP backend user subtree",
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
             "USAGE": "Keystone LDAP backend user query filter",
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
             "USAGE": "Keystone LDAP backend user objectclass",
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
             "USAGE": "Keystone LDAP backend user ID attribute",
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
             "USAGE": "Keystone LDAP backend user name attribute",
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
             "USAGE": "Keystone LDAP backend user email address attribute",
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
             "USAGE": "Keystone LDAP backend user enabled attribute",
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
             "USAGE": (
                 "Keystone LDAP backend - bit mask applied to "
                 "user enabled attribute"
             ),
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
             "USAGE": (
                 "Keystone LDAP backend - value of enabled attribute which "
                 "indicates user is enabled"
             ),
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
             "USAGE": "Keystone LDAP backend - users are disabled not enabled",
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
             "USAGE": (
                 "Comma separated list of attributes stripped "
                 "from user entry upon update"
             ),
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
             "USAGE": (
                 "Keystone LDAP attribute mapped to default_project_id "
                 "for users"
             ),
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

            {"CMD_OPTION": "keystone-ldap-user-allow-create",
             "USAGE": (
                 "Set to 'y' if you want to be able to create Keystone "
                 "users through the Keystone interface.  Set to 'n' if you "
                 "will create directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow user create through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ALLOW_CREATE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-allow-update",
             "USAGE": (
                 "Set to 'y' if you want to be able to update Keystone "
                 "users through the Keystone interface.  Set to 'n' if you "
                 "will update directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow user update through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ALLOW_UPDATE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-allow-delete",
             "USAGE": (
                 "Set to 'y' if you want to be able to delete Keystone "
                 "users through the Keystone interface.  Set to 'n' if you "
                 "will delete directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow user delete through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_USER_ALLOW_DELETE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-user-pass-attribute",
             "USAGE": "Keystone LDAP attribute mapped to password",
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
             "USAGE": (
                 "DN of the group entry to hold enabled users when "
                 "using enabled emulation."
             ),
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
             "USAGE": (
                 'List of additional LDAP attributes used for mapping '
                 'additional attribute mappings for users. Attribute '
                 'mapping format is <ldap_attr>:<user_attr>, where '
                 'ldap_attr is the attribute in the LDAP entry and '
                 'user_attr is the Identity API attribute.'
             ),
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
             "USAGE": "Keystone LDAP backend group subtree",
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
             "USAGE": "Keystone LDAP backend group query filter",
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
             "USAGE": "Keystone LDAP backend group objectclass",
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
             "USAGE": "Keystone LDAP backend group ID attribute",
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
             "USAGE": "Keystone LDAP backend group name attribute",
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
             "USAGE": "Keystone LDAP backend group member attribute",
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
             "USAGE": "Keystone LDAP backend group description attribute",
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
             "USAGE": (
                 "Comma separated list of attributes stripped from "
                 "group entry upon update"
             ),
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

            {"CMD_OPTION": "keystone-ldap-group-allow-create",
             "USAGE": (
                 "Set to 'y' if you want to be able to create Keystone "
                 "groups through the Keystone interface.  Set to 'n' if you "
                 "will create directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow group create through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_CREATE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-allow-update",
             "USAGE": (
                 "Set to 'y' if you want to be able to update Keystone "
                 "groups through the Keystone interface.  Set to 'n' if you "
                 "will update directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow group update through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_UPDATE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-allow-delete",
             "USAGE": (
                 "Set to 'y' if you want to be able to delete Keystone "
                 "groups through the Keystone interface.  Set to 'n' if you "
                 "will delete directly in the LDAP backend."
             ),
             "PROMPT": (
                 "Do you want to allow group delete through Keystone (n or y)."
             ),
             "OPTION_LIST": ['n', 'y'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'n',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_DELETE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "keystone-ldap-group-additional-attribute-mapping",
             "USAGE": (
                 'List of additional LDAP attributes used for mapping '
                 'additional attribute mappings for groups. Attribute '
                 'mapping format is <ldap_attr>:<group_attr>, where '
                 'ldap_attr is the attribute in the LDAP entry and '
                 'group_attr is the Identity API attribute.'
             ),
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
             "USAGE": "Should Keystone LDAP use TLS",
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
             "USAGE": "Keystone LDAP CA certificate directory",
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
             "USAGE": "Keystone LDAP CA certificate file",
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
             "USAGE": (
                 "Keystone LDAP certificate checking strictness "
                 "(never, allow, demand)"
             ),
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
        {'title': 'Adding Keystone manifest entries',
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
            'CONFIG_KEYSTONE_LDAP_USER_ALLOW_CREATE',
            'CONFIG_KEYSTONE_LDAP_USER_ALLOW_UPDATE',
            'CONFIG_KEYSTONE_LDAP_USER_ALLOW_DELETE',
            'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_CREATE',
            'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_UPDATE',
            'CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_DELETE',
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
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone")

    fw_details = dict()
    key = "keystone"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "keystone"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['5000', '35357']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_KEYSTONE_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_KEYSTONE_RULES')
    appendManifestFile(manifestfile, manifestdata)
