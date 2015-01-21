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

import os

from unittest import TestCase
from ..test_base import PackstackTestCaseMixin

from packstack.installer.exceptions import PuppetError
from packstack.modules.puppet import validate_logfile


class PuppetTestCase(PackstackTestCaseMixin, TestCase):

    def test_validate_logfile(self):
        """Test packstack.modules.validate_logfile."""
        filename = os.path.join(self.tempdir, "puppet.log")
        # test valid run
        with open(filename, "w") as fp:
            fp.write("Everything went ok")
        validate_logfile(filename)
        # test invalid run
        with open(filename, "w") as fp:
            fp.write("No matching value for selector param 'Fedora' ...")
        self.assertRaises(PuppetError, validate_logfile, filename)
        # test run with error exception
        with open(filename, "w") as fp:
            err = ("err: Could not prefetch database_grant provider 'mysql': "
                   "Execution of '/usr/bin/mysql --defaults-file=/root/.my.cnf"
                   " mysql -Be describe user' returned 1: Could not open "
                   "required defaults file: /root/.my.cnf")
            fp.write(err)
        validate_logfile(filename)
        # test surrogate
        with open(filename, "w") as fp:
            err = ("err: /Stage[main]/Vswitch::Ovs/Package[openvswitch]/ensure"
                   ": change from absent to present failed: Execution of "
                   "'/usr/bin/yum -d 0 -e 0 -y install openvswitch' returned "
                   "1: Error: Nothing to do")
            fp.write(err)
        self.assertRaises(PuppetError, validate_logfile, filename)
        try:
            validate_logfile(filename)
        except PuppetError as ex:
            ex_msg = str(ex)
            sr_msg = ("Package openvswitch has not been found in enabled Yum "
                      "repos")
            assert sr_msg in ex_msg
