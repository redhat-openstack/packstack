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

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-HORIZON"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Horizon configuration")
    paramsList = [
                  {"CMD_OPTION"      : "os-horizon-host",
                   "USAGE"           : "The IP address of the server on which to install Horizon",
                   "PROMPT"          : "Enter the IP address of the Horizon server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_HORIZON_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-horizon-ssl",
                   "USAGE"           : "To set up Horizon communication over https set this to \"y\"",
                   "PROMPT"          : "Would you like to set up Horizon communication over https",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_HORIZON_SSL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSHORIZON",
                  "DESCRIPTION"           : "OpenStack Horizon Config parameters",
                  "PRE_CONDITION"         : "CONFIG_HORIZON_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    paramsList = [
                  {"CMD_OPTION"      : "os-ssl-cert",
                   "USAGE"           : "PEM encoded certificate to be used for ssl on the https server, leave blank if one should be generated, this certificate should not require a passphrase",
                   "PROMPT"          : "Enter the path to a PEM encoded certificate to be used on the https server, leave blank if one should be generated, this certificate should not require a passphrase",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [],
                   "DEFAULT_VALUE"   : '',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SSL_CERT",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-ssl-key",
                   "USAGE"           : "Keyfile corresponding to the certificate if one was entered",
                   "PROMPT"          : "Enter the keyfile corresponding to the certificate if one was entered",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SSL_KEY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSSSL",
                  "DESCRIPTION"           : "SSL Config parameters",
                  "PRE_CONDITION"         : "CONFIG_HORIZON_SSL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_HORIZON_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Horizon manifest entries', 'functions': [createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)


def createmanifest(config):
    controller.CONF["CONFIG_HORIZON_SECRET_KEY"] = uuid.uuid4().hex
    horizon_host = controller.CONF['CONFIG_HORIZON_HOST']
    manifestfile = "%s_horizon.pp" % horizon_host

    proto = "http"
    controller.CONF["CONFIG_HORIZON_PORT"] = "'80'"
    sslmanifestdata = ''
    if controller.CONF["CONFIG_HORIZON_SSL"] == 'y':
        controller.CONF["CONFIG_HORIZON_PORT"] = "'443'"
        proto = "https"
        sslmanifestdata += getManifestTemplate("https.pp")

        # Are we using the users cert/key files
        if controller.CONF["CONFIG_SSL_CERT"]:
            ssl_cert = controller.CONF["CONFIG_SSL_CERT"]
            ssl_key = controller.CONF["CONFIG_SSL_KEY"]

            if not os.path.exists(ssl_cert):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_cert)

            if ssl_key and not os.path.exists(ssl_key):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_key)

            controller.addResource(horizon_host, ssl_cert, 'ssl_ps_server.crt')
            if ssl_key:
                controller.addResource(
                    horizon_host, ssl_key, 'ssl_ps_server.key'
                )
        else:
            controller.MESSAGES.append(
                "%sNOTE%s : A certificate was generated to be used for ssl, "
                "You should change the ssl certificate configured in "
                "/etc/httpd/conf.d/ssl.conf on %s to use a CA signed cert."
                % (utils.COLORS['red'], utils.COLORS['nocolor'], horizon_host))

    manifestdata = getManifestTemplate("horizon.pp")
    manifestdata += sslmanifestdata
    appendManifestFile(manifestfile, manifestdata)

    msg = "To access the OpenStack Dashboard browse to %s://%s/dashboard.\n" \
          "Please, find your login credentials stored in the keystonerc_admin" \
          " in your home directory." % \
          (proto,  controller.CONF['CONFIG_HORIZON_HOST'])
    controller.MESSAGES.append(msg)
