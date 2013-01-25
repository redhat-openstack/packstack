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

from packstack.modules.ospluginutils import gethostlist, \
                                            validate_puppet_logfile, \
                                            PackStackError


class OSPluginUtilsTestCase(TestCase):
    def test_gethostlist(self):
        conf = {"A_HOST": "1.1.1.1", "B_HOSTS": "2.2.2.2,1.1.1.1",
                "C_HOSTS": "3.3.3.3/vdc"}
        hosts = gethostlist(conf)
        hosts.sort()
        self.assertEquals(['1.1.1.1', '2.2.2.2', '3.3.3.3'], hosts)

    def test_validate_puppet_logfile(self):
        filename = os.path.join(self.tempdir, "puppet.log")
        fp = open(filename, "w")
        fp.write("Everything went ok")
        fp.close()

        validate_puppet_logfile(filename)

    def test_validate_puppet_logfile_error(self):
        filename = os.path.join(self.tempdir, "puppet.log")
        fp = open(filename, "w")
        fp.write("No matching value for selector param 'Fedora' ...")
        fp.close()

        self.assertRaises(PackStackError, validate_puppet_logfile, filename)
