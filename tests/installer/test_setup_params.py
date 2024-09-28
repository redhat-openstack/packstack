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
Test cases for packstack.installer.core.parameters module.
"""

from unittest import TestCase

from ..test_base import PackstackTestCaseMixin
from packstack.installer.core import parameters


class ParameterTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        super(ParameterTestCase, self).setUp()
        self.data = {
            "CMD_OPTION": "mariadb-host",
            "USAGE": ("The IP address of the server on which to "
                      "install MariaDB"),
            "PROMPT": "Enter the IP address of the MariaDB server",
            "OPTION_LIST": [],
            "VALIDATORS": [],
            "DEFAULT_VALUE": "127.0.0.1",
            "MASK_INPUT": False,
            "LOOSE_VALIDATION": True,
            "CONF_NAME": "CONFIG_MARIADB_HOST",
            "USE_DEFAULT": False,
            "NEED_CONFIRM": False,
            "CONDITION": False}

    def test_parameter_init(self):
        """
        Test packstack.installer.core.parameters.Parameter
        initialization
        """
        param = parameters.Parameter(self.data)
        for key, value in self.data.items():
            self.assertEqual(getattr(param, key), value)

    def test_default_attribute(self):
        """
        Test packstack.installer.core.parameters.Parameter default value
        """
        param = parameters.Parameter()
        self.assertIsNone(param.PROCESSORS)


class GroupTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        super(GroupTestCase, self).setUp()
        self.attrs = {
            "GROUP_NAME": "MARIADB",
            "DESCRIPTION": "MariaDB Config parameters",
            "PRE_CONDITION": "y",
            "PRE_CONDITION_MATCH": "y",
            "POST_CONDITION": False,
            "POST_CONDITION_MATCH": False}
        self.params = [
            {"CONF_NAME": "CONFIG_MARIADB_HOST", "PROMPT": "find_me"},
            {"CONF_NAME": "CONFIG_MARIADB_USER"},
            {"CONF_NAME": "CONFIG_MARIADB_PW"}]

    def test_group_init(self):
        """
        Test packstack.installer.core.parameters.Group initialization
        """
        group = parameters.Group(attributes=self.attrs, parameters=self.params)
        for key, value in self.attrs.items():
            self.assertEqual(getattr(group, key), value)
        for param in self.params:
            self.assertIn(param['CONF_NAME'], group.parameters)

    def test_search(self):
        """
        Test packstack.installer.core.parameters.Group search method
        """
        group = parameters.Group(attributes=self.attrs, parameters=self.params)
        param_list = group.search('PROMPT', 'find_me')
        self.assertEqual(len(param_list), 1)
        self.assertIsInstance(param_list[0], parameters.Parameter)
        self.assertEqual(param_list[0].CONF_NAME, 'CONFIG_MARIADB_HOST')
