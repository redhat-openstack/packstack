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
from packstack.installer import exceptions
from packstack.installer import validators

from ..test_base import PackstackTestCaseMixin


class ValidatorsTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)

    def test_validate_integer(self):
        """Test validate_integer."""
        validators.validate_integer('1')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_integer, 'test')

    def test_validate_regexp(self):
        """Test validate_regexp."""
        validators.validate_regexp('Test_123', options=[r'\w'])
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_regexp, '!#$%', options=[r'\w'])

    def test_validate_port(self):
        """Test validate_port."""
        validators.validate_port('666')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_port, 'test')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_port, '-3')

    def test_validate_not_empty(self):
        """Test validate_not_empty."""
        validators.validate_not_empty('test')
        validators.validate_not_empty(False)
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_not_empty, '')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_not_empty, [])
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_not_empty, {})

    def test_validate_options(self):
        """Test validate_options."""
        validators.validate_options('a', options=['a', 'b'])
        validators.validate_options('b', options=['a', 'b'])
        self.assertRaises(
            exceptions.ParamValidationError,
            validators.validate_options, 'c', options=['a', 'b'])

    def test_validate_ip(self):
        """Test validate_ip."""
        validators.validate_ip('127.0.0.1')
        validators.validate_ip('::1')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_ip, 'test')

    def test_validate_file(self):
        """Test validate_file."""
        dname = os.path.join(self.tempdir, '.test_validate_file')
        bad_name = os.path.join(self.tempdir, '.me_no/exists')
        os.mkdir(dname)
        validators.validate_writeable_directory(dname)
        self.assertRaises(
            exceptions.ParamValidationError,
            validators.validate_writeable_directory, bad_name)

    def test_validate_writeable_directory(self):
        """Test validate_writeable_directory."""
        fname = os.path.join(
            self.tempdir, '.test_validate_writeable_directory')
        bad_name = os.path.join(self.tempdir, '.me_no_exists')
        with open(fname, 'w') as f:
            f.write('test')
        validators.validate_file(fname)
        self.assertRaises(
            exceptions.ParamValidationError,
            validators.validate_file, bad_name)

    def test_validate_ping(self):
        """Test validate_ping."""
        # ping to broadcast fails
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_ping, '255.255.255.255')

    def test_validate_ssh(self):
        """Test validate_ssh."""
        # ssh to broadcast fails
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_ssh, '255.255.255.255')

    def test_validate_float(self):
        """Test validate_float."""
        validators.validate_float('5.3')
        self.assertRaises(exceptions.ParamValidationError,
                          validators.validate_float, 'test')
