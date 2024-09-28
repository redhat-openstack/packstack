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

"""
Test cases for packstack.installer.utils module.
"""

import shutil
import tempfile
from unittest import TestCase

from ..test_base import FakePopen
from ..test_base import PackstackTestCaseMixin
from packstack.installer import utils
from packstack.installer.utils.strings import STR_MASK
from packstack.installer.exceptions import ExecuteRuntimeError


cnt = 0


class ParameterTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()
        FakePopen.register('echo "this is test"',
                           stdout='this is test')

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)

    def test_sorteddict(self):
        """Test packstack.installer.utils.datastructures.SortedDict."""
        sdict = utils.SortedDict()
        sdict['1'] = 1
        sdict['2'] = 2
        sdict.update(utils.SortedDict([('3', 3), ('4', 4), ('5', 5)]))
        self.assertListEqual(sdict.keys(), ['1', '2', '3', '4', '5'])
        self.assertListEqual(sdict.values(), [1, 2, 3, 4, 5])

    def test_retry(self):
        """Test packstack.installer.utils.decorators.retry."""

        @utils.retry(count=3, delay=0, retry_on=ValueError)
        def test_sum():
            global cnt
            cnt += 1
            raise ValueError

        global cnt
        cnt = 0

        try:
            test_sum()
        except ValueError:
            pass
        self.assertEqual(cnt, 4)
        self.assertRaises(ValueError, test_sum)

    def test_network(self):
        """Test packstack.installer.utils.network functions."""
        self.assertIn(utils.host2ip('localhost', allow_localhost=True),
                      ['127.0.0.1', '::1'])

    def test_shell(self):
        """Test packstack.installer.utils.shell functions."""
        rc, out = utils.execute(['echo', 'this is test'])
        self.assertEqual(out.strip(), 'this is test')
        rc, out = utils.execute('echo "this is test"', use_shell=True)
        self.assertEqual(out.strip(), 'this is test')
        try:
            utils.execute('echo "mask the password" && exit 1',
                          use_shell=True, mask_list=['password'])
            raise AssertionError('Masked execution failed.')
        except ExecuteRuntimeError as ex:
            should_be = ('Failed to execute command, stdout: mask the %s\n\n'
                         'stderr: ' % STR_MASK)
            self.assertEqual(str(ex), should_be)

        script = utils.ScriptRunner()
        script.append('echo "this is test"')
        rc, out = script.execute()
        self.assertEqual(out.strip(), 'this is test')

    def test_strings(self):
        """Test packstack.installer.utils.strings functions."""
        self.assertEqual(utils.color_text('test text', 'red'),
                         '\033[0;31mtest text\033[0m')
        self.assertEqual(utils.mask_string('test text', mask_list=['text']),
                         'test %s' % STR_MASK)
        masked = utils.mask_string("test '\\''text'\\''",
                                   mask_list=["'text'"],
                                   replace_list=[("'", "'\\''")])
        self.assertEqual(masked, 'test %s' % STR_MASK)

    def test_shortcuts(self):
        """Test packstack.installer.utils.shortcuts functions."""
        conf = {"A_HOST": "1.1.1.1", "B_HOSTS": "2.2.2.2,1.1.1.1",
                "C_HOSTS": "3.3.3.3/vdc"}
        hostlist = list(utils.hosts(conf))
        hostlist.sort()
        self.assertEqual(['1.1.1.1', '2.2.2.2', '3.3.3.3'], hostlist)
