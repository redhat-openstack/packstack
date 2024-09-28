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

import logging
import shutil
import subprocess
import tempfile


LOG = logging.getLogger(__name__)


class FakePopen(object):
    '''The FakePopen class replaces subprocess.Popen. Instead of actually
    executing commands, it permits the caller to register a list of
    commands the output to produce using the FakePopen.register and
    FakePopen.register_as_script method.  By default, FakePopen will return
    empty stdout and stderr and a successful (0) returncode.
    '''

    cmd_registry = {}
    script_registry = {}

    @classmethod
    def register(cls, args, stdout='', stderr='', returncode=0):
        '''Register a fake command.'''
        if isinstance(args, list):
            args = tuple(args)
        cls.cmd_registry[args] = {'stdout': stdout,
                                  'stderr': stderr,
                                  'returncode': returncode}

    @classmethod
    def register_as_script(cls, args, stdout='', stderr='', returncode=0):
        '''Register a fake script.'''
        if isinstance(args, list):
            args = '\n'.join(args)

        prefix = "function t(){ exit $? ; } \n trap t ERR \n "
        args = prefix + args
        cls.script_registry[args] = {'stdout': stdout,
                                     'stderr': stderr,
                                     'returncode': returncode}

    def __init__(self, args, **kwargs):
        script = ["ssh", "-o", "StrictHostKeyChecking=no",
                  "-o", "UserKnownHostsFile=/dev/null"]
        if args[-1] == "bash -x" and args[:5] == script:
            self._init_as_script(args, **kwargs)
        else:
            self._init_as_cmd(args, **kwargs)

    def _init_as_cmd(self, args, **kwargs):
        self._is_script = False
        if isinstance(args, list):
            args = tuple(args)
            cmd = ' '.join(args)
        else:
            cmd = args

        if args in self.cmd_registry:
            this = self.cmd_registry[args]
        else:
            LOG.warning('call to unregistered command: %s', cmd)
            this = {'stdout': '', 'stderr': '', 'returncode': 0}

        self.stdout = this['stdout']
        self.stderr = this['stderr']
        self.returncode = this['returncode']

    def _init_as_script(self, args, **kwargs):
        self._is_script = True

    def communicate(self, input=None):
        if self._is_script:
            if input.decode('utf-8') in self.script_registry:
                this = self.script_registry[input.decode('utf-8')]
            else:
                LOG.warning('call to unregistered script: %s', input)
                this = {'stdout': '', 'stderr': '', 'returncode': 0}
            self.stdout = this['stdout']
            self.stderr = this['stderr']
            self.returncode = this['returncode']
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
        self.fake_popen = subprocess.Popen = FakePopen

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)
        subprocess.Popen = self._Popen

    def assertItemsEqual(self, list1, list2, msg=None):
        f, s = len(list1), len(list2)
        _msg = msg or ('Element counts were not equal. First has %s, '
                       'Second has %s' % (f, s))
        self.assertEqual(f, s, msg=_msg)

        _msg = msg or f'Given lists differ:\n{list1}\n{list2}'
        for i in list1:
            if i not in list2:
                raise AssertionError(_msg)

    def assertListEqual(self, list1, list2, msg=None):
        f, s = len(list(list1)), len(list(list2))
        _msg = msg or ('Element counts were not equal. First has %s, '
                       'Second has %s' % (f, s))
        self.assertEqual(f, s, msg=_msg)

        _msg = msg or f'Given lists differ:\n{list1}\n{list2}'
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
