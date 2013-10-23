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
from unittest import TestCase

from test_base import PackstackTestCaseMixin
from packstack.plugins import serverprep_949
from packstack.installer.setup_controller import Controller

serverprep_949.controller = Controller()


class OSPluginUtilsTestCase(PackstackTestCaseMixin, TestCase):
    def test_rhn_creds_quoted(self):
        """Make sure RHN password is quoted"""

        # On non-RHEL, the CONFIG_{RH,SATELLITE} options are never set,
        # i.e. this test would always fail. Therefore, only run it on RHEL.
        if not serverprep_949.is_rhel():
            return

        password = "dasd|'asda%><?"

        serverprep_949.controller.CONF["CONFIG_KEYSTONE_HOST"] = "1.2.3.4"
        serverprep_949.controller.CONF["CONFIG_USE_EPEL"] = "n"
        serverprep_949.controller.CONF["CONFIG_REPO"] = ""
        serverprep_949.controller.CONF["CONFIG_RH_USER"] = "testuser"
        serverprep_949.controller.CONF["CONFIG_RH_PW"] = password
        serverprep_949.controller.CONF["CONFIG_RH_BETA_REPO"] = "n"

        serverprep_949.controller.CONF["CONFIG_SATELLITE_FLAGS"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_URL"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_USER"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_PW"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_CACERT"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_AKEY"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_PROFILE"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_PROXY"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_PROXY_USER"] = ""
        serverprep_949.controller.CONF["CONFIG_SATELLITE_PROXY_PW"] = ""

        serverprep_949.serverprep(serverprep_949.controller.CONF)

        self.assertNotEqual(
            self.fake_popen.data.find('--password="%s"' % password), -1
        )
