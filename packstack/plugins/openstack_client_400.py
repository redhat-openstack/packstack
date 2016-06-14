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
Installs and configures an OpenStack Client
"""

import os

from packstack.installer import utils

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
        {'title': 'Preparing OpenStack Client entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Client", [], [],
                           osclientsteps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    client_host = config['CONFIG_CONTROLLER_HOST'].strip()

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

    msg = ("File %s/keystonerc_admin has been created on OpenStack client host"
           " %s. To use the command line tools you need to source the file.")
    messages.append(msg % (root_home, client_host))

    if no_root_allinone:
        msg = ("Copy of keystonerc_admin file has been created for non-root "
               "user in %s.")
        messages.append(msg % homedir)
