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

import shutil
import tempfile
import subprocess


class FakePopen(object):
    def __init__(self, returncode=0):
        self.returncode = returncode
        self.stdout = self.stderr = self.data = ""

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def communicate(self, data=None):
        self.data += data or ''
        return self.stdout, self.stderr


class PackstackTestCaseMixin(object):
    """
    Implementation of some assertion methods available by default
    in Python2.7+ only
    """
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()

        # some plugins call popen, we're replacing it for tests
        self._Popen = subprocess.Popen
        self.fake_popen = subprocess.Popen = FakePopen()

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)
        subprocess.Popen = self._Popen

    def assertItemsEqual(self, list1, list2, msg=None):
        f, s = len(list1), len(list2)
        _msg = msg or ('Element counts were not equal. First has %s, '
                       'Second has %s' % (f, s))
        self.assertEqual(f, s, msg=_msg)

        _msg = msg or ('Given lists differ:\n%(list1)s'
                       '\n%(list2)s' % locals())
        for i in list1:
            if i not in list2:
                raise AssertionError(_msg)

    def assertListEqual(self, list1, list2, msg=None):
        f, s = len(list1), len(list2)
        _msg = msg or ('Element counts were not equal. First has %s, '
                       'Second has %s' % (f, s))
        self.assertEqual(f, s, msg=_msg)

        _msg = msg or ('Given lists differ:\n%(list1)s'
                       '\n%(list2)s' % locals())
        for index, item in enumerate(list1):
            if item != list2[index]:
                raise AssertionError(_msg)

    def assertIsInstance(self, obj, cls, msg=None):
        _msg = msg or ('%s is not an instance of %s' % (obj, cls))
        if not isinstance(obj, cls):
            raise AssertionError(_msg)

    def assertIn(self, first, second, msg=None):
        _msg = msg or ('%s is not a member of %s' % (first, second))
        if first not in second:
            raise AssertionError(_msg)

    def assertIsNone(self, expr, msg=None):
        _msg = msg or ('%s is not None' % expr)
        if expr is not None:
            raise AssertionError(_msg)
