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
Plugin responsible for post-installation configuration
"""

from packstack.installer import utils
from packstack.installer import basedefs


# ------------- Postscript Packstack Plugin Initialization --------------

PLUGIN_NAME = "Postscript"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    group = {"GROUP_NAME": "POSTSCRIPT",
             "DESCRIPTION": "POSTSCRIPT Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, [])


def initSequences(controller):
    config = controller.CONF
    postscript_steps = []
    if (config['CONFIG_PROVISION_TEMPEST'] == "y" and
            config['CONFIG_RUN_TEMPEST'] == "y"):
        postscript_steps.append(
            {'title': 'Running Tempest',
             'functions': [run_tempest]}
        )
    controller.addSequence("Running post install scripts", [], [],
                           postscript_steps)


# -------------------------- step functions --------------------------

def run_tempest(config, messages):
    logfile = basedefs.DIR_LOG + "/tempest.log"
    print("Running Tempest on %s" % config['CONFIG_TEMPEST_HOST'])
    server = utils.ScriptRunner(config['CONFIG_TEMPEST_HOST'])
    server.append('pushd /var/lib/tempest')
    server.append('tempest run --regex \'(%s)\' --black-regex \'%s\' --concurrency 2  > %s'
                  % (config['CONFIG_RUN_TEMPEST_TESTS'].replace(' ', '|'),
                     config['CONFIG_SKIP_TEMPEST_TESTS'].replace(' ', '|'),
                     logfile))
    server.append('popd')
    server.execute()
