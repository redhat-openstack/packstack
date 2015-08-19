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

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import getManifestTemplate

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
    postscript_steps = [
        {'title': 'Adding post install manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Running post install scripts", [], [],
                           postscript_steps)


# -------------------------- step functions --------------------------

def create_manifest(config, messages):
    for hostname in filtered_hosts(config):
        manifestfile = "%s_postscript.pp" % hostname
        manifestdata = getManifestTemplate("postscript")
        appendManifestFile(manifestfile, manifestdata, 'postscript')
