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

from unittest import TestCase

from test_base import PackstackTestCaseMixin
from packstack.plugins import prescript_000


class OSPluginUtilsTestCase(PackstackTestCaseMixin, TestCase):
    def test_rhn_creds_quoted(self):
        """Make sure RHN password is quoted."""

        # On non-RHEL, the CONFIG_{RH,SATELLITE} options are never set,
        # i.e. this test would always fail. Therefore, only run it on RHEL.
        if not prescript_000.is_rhel():
            return

        password = "dasd|'asda%><?"

        prescript_000.controller.CONF["CONFIG_KEYSTONE_HOST"] = "1.2.3.4"
        prescript_000.controller.CONF["CONFIG_USE_EPEL"] = "n"
        prescript_000.controller.CONF["CONFIG_REPO"] = ""
        prescript_000.controller.CONF["CONFIG_RH_USER"] = "testuser"
        prescript_000.controller.CONF["CONFIG_RH_PW"] = password
        prescript_000.controller.CONF["CONFIG_RH_BETA_REPO"] = "n"

        prescript_000.controller.CONF["CONFIG_SATELLITE_FLAGS"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_URL"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_USER"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_PW"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_CACERT"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_AKEY"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_PROFILE"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_PROXY"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_PROXY_USER"] = ""
        prescript_000.controller.CONF["CONFIG_SATELLITE_PROXY_PW"] = ""

        prescript_000.serverprep(prescript_000.controller.CONF)

        self.assertNotEqual(
            self.fake_popen.data.find('--password="%s"' % password), -1
        )
