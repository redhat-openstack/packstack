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
import shutil
import tempfile
from unittest import TestCase
from packstack.installer.validators import *

from ..test_base import PackstackTestCaseMixin


class ValidatorsTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)

    def test_validate_integer(self):
        """Test packstack.installer.validators.validate_integer."""
        validate_integer('1')
        self.assertRaises(ParamValidationError, validate_integer, 'test')

    def test_validate_regexp(self):
        """Test packstack.installer.validators.validate_regexp."""
        validate_regexp('Test_123', options=['\w'])
        self.assertRaises(ParamValidationError, validate_regexp,
                          '!#$%', options=['\w'])

    def test_validate_port(self):
        """Test packstack.installer.validators.validate_port."""
        validate_port('666')
        self.assertRaises(ParamValidationError, validate_port, 'test')
        self.assertRaises(ParamValidationError, validate_port, '-3')

    def test_validate_not_empty(self):
        """Test packstack.installer.validators.validate_not_empty."""
        validate_not_empty('test')
        validate_not_empty(False)
        self.assertRaises(ParamValidationError, validate_not_empty, '')
        self.assertRaises(ParamValidationError, validate_not_empty, [])
        self.assertRaises(ParamValidationError, validate_not_empty, {})

    def test_validate_options(self):
        """Test packstack.installer.validators.validate_options."""
        validate_options('a', options=['a', 'b'])
        validate_options('b', options=['a', 'b'])
        self.assertRaises(ParamValidationError, validate_options,
                          'c', options=['a', 'b'])

    def test_validate_ip(self):
        """Test packstack.installer.validators.validate_ip."""
        validate_ip('127.0.0.1')
        validate_ip('::1')
        self.assertRaises(ParamValidationError, validate_ip, 'test')

    def test_validate_file(self):
        """Test packstack.installer.validators.validate_file."""
        dname = os.path.join(self.tempdir, '.test_validate_file')
        bad_name = os.path.join(self.tempdir, '.me_no/exists')
        os.mkdir(dname)
        validate_writeable_directory(dname)
        self.assertRaises(ParamValidationError, validate_writeable_directory, bad_name)

    def test_validate_writeable_directory(self):
        """Test packstack.installer.validators.validate_writeable_directory."""
        fname = os.path.join(self.tempdir, '.test_validate_writeable_directory')
        bad_name = os.path.join(self.tempdir, '.me_no_exists')
        with open(fname, 'w') as f:
            f.write('test')
        validate_file(fname)
        self.assertRaises(ParamValidationError, validate_file, bad_name)

    def test_validate_ping(self):
        """Test packstack.installer.validators.validate_ping."""
        # ping to broadcast fails
        self.assertRaises(ParamValidationError, validate_ping,
                          '255.255.255.255')

    def test_validate_ssh(self):
        """Test packstack.installer.validators.validate_ssh."""
        # ssh to broadcast fails
        self.assertRaises(ParamValidationError, validate_ssh,
                          '255.255.255.255')

    def test_validate_float(self):
        """Test packstack.installer.validators.validate_float."""
        validate_float('5.3')
        self.assertRaises(ParamValidationError, validate_float, 'test')
