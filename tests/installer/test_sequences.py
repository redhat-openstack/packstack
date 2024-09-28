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

import io
import sys
from unittest import TestCase

from packstack.installer import utils
from packstack.installer.core import sequences

from ..test_base import PackstackTestCaseMixin


class StepTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        super(StepTestCase, self).setUp()
        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        super(StepTestCase, self).tearDown()
        sys.stdout = self._stdout

    def test_run(self):
        """
        Test packstack.instaler.core.sequences.Step run.
        """
        def func(config, messages):
            if 'test' not in config:
                raise AssertionError('Missing config value.')

        step = sequences.Step('test', func, title='Running test')
        step.run(config={'test': 'test'})
        contents = sys.stdout.getvalue()

        state = '[ %s ]\n' % utils.color_text('DONE', 'green')
        if (not contents.startswith('Running test') or
                not contents.endswith(state)):
            raise AssertionError('Step run test failed: %s' % contents)


class SequenceTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        super(SequenceTestCase, self).setUp()
        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

        self.steps = [{'name': '1', 'function': lambda x, y: True,
                       'title': 'Step 1'},
                      {'name': '2', 'function': lambda x, y: True,
                       'title': 'Step 2'},
                      {'name': '3', 'function': lambda x, y: True,
                       'title': 'Step 3'}]

        self.seq = sequences.Sequence('test', self.steps, condition='test',
                                      cond_match='test')

    def tearDown(self):
        super(SequenceTestCase, self).tearDown()
        sys.stdout = self._stdout

    def test_run(self):
        """
        Test packstack.instaler.core.sequences.Sequence run.
        """
        self.seq.run()
        contents = sys.stdout.getvalue()
        self.assertEqual(contents, '')

        self.seq.run(config={'test': 'test'}, step='2')
        contents = sys.stdout.getvalue()
        assert contents.startswith('Step 2')

        output = []
        self.steps.insert(0, {'title': 'Step 2'})
        for i in self.steps:
            output.append('%s\n' % utils.state_message(i['title'],
                                                       'DONE', 'green'))

        self.seq.run(config={'test': 'test'})
        contents = sys.stdout.getvalue()
        self.assertEqual(contents, ''.join(output))
