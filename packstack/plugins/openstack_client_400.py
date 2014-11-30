# -*- coding: utf-8 -*-

"""
Installs and configures an OpenStack Client
"""

import os

from packstack.installer import utils

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


# ------------- OpenStack Client Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Client"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    group = {"GROUP_NAME": "NOVACLIENT",
             "DESCRIPTION": "NOVACLIENT Config parameters",
             "PRE_CONDITION": "CONFIG_CLIENT_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, [])


def initSequences(controller):
    if controller.CONF['CONFIG_CLIENT_INSTALL'] != 'y':
        return

    osclientsteps = [
        {'title': 'Adding OpenStack Client manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Client", [], [],
                           osclientsteps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    client_host = config['CONFIG_CONTROLLER_HOST'].strip()
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
    config['NO_ROOT_USER_ALLINONE'] = no_root_allinone and True or False

    manifestdata = getManifestTemplate("openstack_client.pp")
    appendManifestFile(manifestfile, manifestdata)

    msg = ("File %s/keystonerc_admin has been created on OpenStack client host"
           " %s. To use the command line tools you need to source the file.")
    messages.append(msg % (root_home, client_host))

    if no_root_allinone:
        msg = ("Copy of keystonerc_admin file has been created for non-root "
               "user in %s.")
        messages.append(msg % homedir)
