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
from unittest import TestCase


class fakePopen(object):
    def __init__(self, returncode=0):
        self.returncode = returncode
        self.stdout = self.stderr = self.data = ""

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def communicate(self, data):
        self.data += data
        return self.stdout, self.stderr


class TestCase(TestCase):
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()

        # some plugins call popen, we're replacing it for tests
        self._Popen = subprocess.Popen
        self.fakePopen = subprocess.Popen = fakePopen()

    def tearDown(self):
        # remove the temp directory
        shutil.rmtree(self.tempdir)

        subprocess.Popen = self._Popen
