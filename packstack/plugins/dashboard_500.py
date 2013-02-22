"""
Installs and configures OpenStack Horizon
"""

import logging
import uuid

import packstack.installer.engine_validators as validate
import packstack.installer.engine_processors as process
from packstack.installer import basedefs, output_messages
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-HORIZON"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

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
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
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
                   "VALIDATORS"      : [validate.validate_options],
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


def initSequences(controller):
    if controller.CONF['CONFIG_HORIZON_INSTALL'] != 'y':
        return

    steps = [
             {'title': 'Adding Horizon manifest entries', 'functions': [createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Horizon", [], [], steps)


def createmanifest():
    controller.CONF["CONFIG_HORIZON_SECRET_KEY"] = uuid.uuid4().hex
    horizon_host = controller.CONF['CONFIG_HORIZON_HOST']
    manifestfile = "%s_horizon.pp" % horizon_host

    proto = "http"
    controller.CONF["CONFIG_HORIZON_PORT"] = "'80'"
    sslmanifestdata = ''
    if controller.CONF["CONFIG_HORIZON_SSL"] == 'y':
        controller.CONF["CONFIG_HORIZON_PORT"] = "'443'"
        controller.MESSAGES.append(
            "%sNOTE%s : A default self signed certificate was used for ssl, "
            "You should change the ssl certificate configured in "
            "/etc/httpd/conf.d/ssl.conf on %s to use a CA signed cert."
            % (basedefs.RED, basedefs.NO_COLOR, horizon_host))
        proto = "https"
        sslmanifestdata += ("class {'apache::mod::ssl': }\n"
                            "file {'/etc/httpd/conf.d/ssl.conf':}\n")

    manifestdata = getManifestTemplate("horizon.pp")
    manifestdata += sslmanifestdata
    appendManifestFile(manifestfile, manifestdata)

    msg = "To use the console, browse to %s://%s/dashboard" % \
        (proto,  controller.CONF['CONFIG_HORIZON_HOST'])
    controller.MESSAGES.append(msg)
