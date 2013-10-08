"""
Installs and configures an OpenStack Client
"""

import logging
import os

from packstack.installer import validators
from packstack.installer import basedefs, output_messages
from packstack.installer import utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-CLIENT"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Client configuration")
    paramsList = [
                  {"CMD_OPTION"      : "osclient-host",
                   "USAGE"           : "The IP address of the server on which to install the OpenStack client packages. An admin \"rc\" file will also be installed",
                   "PROMPT"          : "Enter the IP address of the client server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_OSCLIENT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NOVACLIENT",
                  "DESCRIPTION"           : "NOVACLIENT Config parameters",
                  "PRE_CONDITION"         : "CONFIG_CLIENT_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CLIENT_INSTALL'] != 'y':
        return

    osclientsteps = [
             {'title': 'Adding OpenStack Client manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Client", [], [], osclientsteps)


def createmanifest(config):
    client_host = config['CONFIG_OSCLIENT_HOST'].strip()
    manifestfile = "%s_osclient.pp" % client_host

    server = utils.ScriptRunner(client_host)
    server.append('echo $HOME')
    rc, root_home = server.execute()
    root_home = root_home.strip()

    homedir = os.path.expanduser('~')
    config['HOME_DIR'] = homedir

    uname, gname = utils.get_current_username()
    config['NO_ROOT_USER'], config['NO_ROOT_GROUP'] = uname, gname

    no_root_allinone = (client_host == utils.get_localhost_ip() and
                        root_home != homedir)
    config['NO_ROOT_USER_ALLINONE'] = no_root_allinone and 'true' or 'false'

    manifestdata = getManifestTemplate("openstack_client.pp")
    appendManifestFile(manifestfile, manifestdata)

    msg = ("File %s/keystonerc_admin has been created on OpenStack client host"
           " %s. To use the command line tools you need to source the file.")
    controller.MESSAGES.append(msg % (root_home, client_host))

    if no_root_allinone:
        msg = ("Copy of keystonerc_admin file has been created for non-root "
               "user in %s.")
        controller.MESSAGES.append(msg % homedir)
