# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
from test import TestCase

from packstack.plugins import serverprep_901
from packstack.installer.setup_controller import Controller

serverprep_901.controller = Controller()


class OSPluginUtilsTestCase(TestCase):
    def test_rhn_creds_quoted(self):
        """Make sure RHN password is quoted"""

        password = "dasd|'asda%><?"
        serverprep_901.controller.CONF["CONFIG_KEYSTONE_HOST"] = "1.2.3.4"
        serverprep_901.controller.CONF["CONFIG_USE_EPEL"] = "n"
        serverprep_901.controller.CONF["CONFIG_REPO"] = ""
        serverprep_901.controller.CONF["CONFIG_RH_USERNAME"] = "testuser"
        serverprep_901.controller.CONF["CONFIG_RH_PASSWORD"] = password

        serverprep_901.serverprep()

        self.assertNotEqual(
            self.fakePopen.data.find('--password="%s"' % password), -1
        )
