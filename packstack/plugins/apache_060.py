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
Installs and configures Apache for all services using it
"""

from packstack.installer import utils

from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import getManifestTemplate

# ------------- Aodh Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Apache"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    # No config needed
    return


def initSequences(controller):
    steps = [{'title': 'Adding Apache manifest entries',
              'functions': [create_manifest]}]
    controller.addSequence("Setting up Apache", [], [],
                           steps)

# ------------------------- step functions -------------------------


def create_manifest(config, messages):
    manifestfile = "%s_apache.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("apache")
    appendManifestFile(manifestfile, manifestdata, 'apache')
