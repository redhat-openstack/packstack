# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2017, Red Hat, Inc.
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

"""
Test cases for packstack.installer.core.arch module.
"""

from unittest import mock
from unittest import TestCase

from packstack.installer.core import arch


class ArchTestCase(TestCase):
    def test_kernel_arch(self):
        for (expected, _arch) in [('x86_64', 'x86_64'),
                                  ('ppc64le', 'ppc64le')]:
            with mock.patch('os.uname', return_value=('', '', '', '', _arch)):
                self.assertEqual(expected, arch.kernel_arch())

    def test_dib_arch(self):
        for (expected, _arch) in [('amd64', 'x86_64'),
                                  ('ppc64le', 'ppc64le')]:
            with mock.patch('os.uname', return_value=('', '', '', '', _arch)):
                self.assertEqual(expected, arch.dib_arch())

    def test_cirros_arch(self):
        for (expected, _arch) in [('x86_64', 'x86_64'),
                                  ('powerpc', 'ppc64le')]:
            with mock.patch('os.uname', return_value=('', '', '', '', _arch)):
                self.assertEqual(expected, arch.cirros_arch())
