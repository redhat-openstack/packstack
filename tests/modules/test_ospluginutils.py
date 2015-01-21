# -*- coding: utf-8 -*-
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

from ..test_base import PackstackTestCaseMixin
from packstack.modules.ospluginutils import gethostlist


class OSPluginUtilsTestCase(PackstackTestCaseMixin, TestCase):
    def test_gethostlist(self):
        conf = {"A_HOST": "1.1.1.1", "B_HOSTS": "2.2.2.2,1.1.1.1",
                "C_HOSTS": "3.3.3.3/vdc"}
        hosts = gethostlist(conf)
        hosts.sort()
        self.assertEqual(['1.1.1.1', '2.2.2.2', '3.3.3.3'], hosts)
