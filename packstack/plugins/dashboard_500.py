# -*- coding: utf-8 -*-

"""
Installs and configures OpenStack Horizon
"""

import logging
import os
import uuid

from packstack.installer import validators
from packstack.installer import basedefs, output_messages
from packstack.installer import exceptions
from packstack.installer import utils

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Horizon"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "os-horizon-ssl",
         "USAGE": "To set up Horizon communication over https set this to 'y'",
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
    ]
    group = {"GROUP_NAME": "OSHORIZON",
             "DESCRIPTION": "OpenStack Horizon Config parameters",
             "PRE_CONDITION": "CONFIG_HORIZON_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    params = [
        {"CMD_OPTION": "os-ssl-cert",
         "USAGE": ("PEM encoded certificate to be used for ssl on the https "
                   "server, leave blank if one should be generated, this "
                   "certificate should not require a passphrase"),
         "PROMPT": ("Enter the path to a PEM encoded certificate to be used "
                    "on the https server, leave blank if one should be "
                    "generated, this certificate should not require "
                    "a passphrase"),
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": '',
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SSL_CERT",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "os-ssl-key",
         "USAGE": ("SSL keyfile corresponding to the certificate if one was "
                   "entered"),
         "PROMPT": ("Enter the SSL keyfile corresponding to the certificate "
                    "if one was entered"),
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_SSL_KEY",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
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
        {'title': 'Adding Horizon manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    config["CONFIG_HORIZON_SECRET_KEY"] = uuid.uuid4().hex
    horizon_host = config['CONFIG_CONTROLLER_HOST']
    manifestfile = "%s_horizon.pp" % horizon_host

    proto = "http"
    config["CONFIG_HORIZON_PORT"] = "'80'"
    sslmanifestdata = ''
    if config["CONFIG_HORIZON_SSL"] == 'y':
        config["CONFIG_HORIZON_PORT"] = "'443'"
        proto = "https"
        sslmanifestdata += getManifestTemplate("https.pp")

        # Are we using the users cert/key files
        if config["CONFIG_SSL_CERT"]:
            ssl_cert = config["CONFIG_SSL_CERT"]
            ssl_key = config["CONFIG_SSL_KEY"]

            if not os.path.exists(ssl_cert):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_cert)

            if ssl_key and not os.path.exists(ssl_key):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_key)

            resources = config.setdefault('RESOURCES', {})
            host_resources = resources.setdefault(horizon_host, [])
            host_resources.append((ssl_cert, 'ssl_ps_server.crt'))
            if ssl_key:
                host_resources.append(ssl_key, 'ssl_ps_server.key')
        else:
            messages.append(
                "%sNOTE%s : A certificate was generated to be used for ssl, "
                "You should change the ssl certificate configured in "
                "/etc/httpd/conf.d/ssl.conf on %s to use a CA signed cert."
                % (utils.COLORS['red'], utils.COLORS['nocolor'], horizon_host))

    manifestdata = getManifestTemplate("horizon.pp")
    manifestdata += sslmanifestdata
    appendManifestFile(manifestfile, manifestdata)

    msg = ("To access the OpenStack Dashboard browse to %s://%s/dashboard .\n"
           "Please, find your login credentials stored in the keystonerc_admin"
           " in your home directory."
           % (proto, config['CONFIG_CONTROLLER_HOST']))
    messages.append(msg)
