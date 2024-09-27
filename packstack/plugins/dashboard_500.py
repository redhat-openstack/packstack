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
Installs and configures OpenStack Horizon
"""

import os
import uuid

from packstack.installer import basedefs
from packstack.installer import exceptions
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import generate_ssl_cert
from packstack.modules.ospluginutils import deliver_ssl_file

# ------------- Horizon Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Horizon"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "os-horizon-ssl",
         "PROMPT": "Would you like to set up Horizon communication over https",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_HORIZON_SSL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-horizon-secretkey",
         "PROMPT": "Horizon Secret Encryption Key",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex,
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_HORIZON_SECRET_KEY",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "OSHORIZON",
             "DESCRIPTION": "OpenStack Horizon Config parameters",
             "PRE_CONDITION": "CONFIG_HORIZON_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    params = [
        {"CMD_OPTION": "os-ssl-cert",
         "PROMPT": ("Enter the path to a PEM encoded certificate to be used "
                    "on the https server, leave blank if one should be "
                    "generated, this certificate should not require "
                    "a passphrase"),
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": '',
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_HORIZON_SSL_CERT",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_SSL_CERT']},

        {"CMD_OPTION": "os-ssl-key",
         "PROMPT": ("Enter the SSL keyfile corresponding to the certificate "
                    "if one was entered"),
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_HORIZON_SSL_KEY",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_SSL_KEY']},

        {"CMD_OPTION": "os-ssl-cachain",
         "PROMPT": ("Enter the CA chain file corresponding to the certificate "
                    "if one was entered"),
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_HORIZON_SSL_CACERT",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_SSL_CACHAIN']},
    ]
    update_params_usage(basedefs.PACKSTACK_DOC, params, sectioned=False)
    group = {"GROUP_NAME": "OSSSL",
             "DESCRIPTION": "SSL Config parameters",
             "PRE_CONDITION": "CONFIG_HORIZON_SSL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_HORIZON_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Preparing Horizon entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    horizon_host = config['CONFIG_CONTROLLER_HOST']

    proto = "http"
    config["CONFIG_HORIZON_PORT"] = 80
    if config["CONFIG_HORIZON_SSL"] == 'y':
        config["CONFIG_HORIZON_PORT"] = 443
        proto = "https"

        # Are we using the users cert/key files
        if config["CONFIG_HORIZON_SSL_CERT"]:
            ssl_cert_file = config["CONFIG_HORIZON_SSL_CERT"]
            ssl_key_file = config["CONFIG_HORIZON_SSL_KEY"]
            ssl_chain_file = config["CONFIG_HORIZON_SSL_CACERT"]

            if not os.path.exists(ssl_cert_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_cert_file)

            if not os.path.exists(ssl_key_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_key_file)

            if not os.path.exists(ssl_chain_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_chain_file)

            final_cacert = open(ssl_chain_file, 'rt').read()
            final_cert = open(ssl_cert_file, 'rt').read()
            final_key = open(ssl_key_file, 'rt').read()
            host = config['CONFIG_CONTROLLER_HOST']
            deliver_ssl_file(final_cacert, ssl_chain_file, host)
            deliver_ssl_file(final_cert, ssl_cert_file, host)
            deliver_ssl_file(final_key, ssl_key_file, host)

        else:
            ssl_cert_file = config["CONFIG_HORIZON_SSL_CERT"] = (
                '/etc/pki/tls/certs/ssl_dashboard.crt'
            )
            ssl_key_file = config["CONFIG_HORIZON_SSL_KEY"] = (
                '/etc/pki/tls/private/ssl_dashboard.key'
            )
            cacert = config['CONFIG_SSL_CACERT']
            config["CONFIG_HORIZON_SSL_CACERT"] = cacert
            ssl_host = config['CONFIG_CONTROLLER_HOST']
            service = 'dashboard'
            generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                              ssl_cert_file)
            messages.append(
                "%sNOTE%s : A certificate was generated to be used for ssl, "
                "You should change the ssl certificate configured in "
                "/etc/httpd/conf.d/ssl.conf on %s to use a CA signed cert."
                % (utils.COLORS['red'], utils.COLORS['nocolor'], horizon_host))

    config["CONFIG_HORIZON_NEUTRON_VPN"] = False

    if config['CONFIG_NEUTRON_INSTALL'] == 'y':
        if config["CONFIG_NEUTRON_VPNAAS"] == 'y':
            config["CONFIG_HORIZON_NEUTRON_VPN"] = True

    msg = ("To access the OpenStack Dashboard browse to %s://%s/dashboard .\n"
           "Please, find your login credentials stored in the keystonerc_admin"
           " in your home directory."
           % (proto, config['CONFIG_CONTROLLER_HOST']))
    messages.append(msg)
