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

import distro
import os
import shutil
import subprocess
import sys
from unittest import TestCase

from packstack.modules import ospluginutils
from packstack.modules import puppet
from packstack.installer import basedefs
from packstack.installer import run_setup
from packstack.installer import validators

from ..test_base import FakePopen
from ..test_base import PackstackTestCaseMixin


def makefile(path, content):
    '''Create the named file with the specified content.'''
    with open(path, 'w') as fd:
        fd.write(content)


class CommandLineTestCase(PackstackTestCaseMixin, TestCase):

    def setUp(self):
        super(CommandLineTestCase, self).setUp()
        self._old_validate_ssh = validators.validate_ssh
        validators.validate_ssh = lambda param, options=None: None

    def tearDown(self):
        super(CommandLineTestCase, self).tearDown()
        validators.validate_ssh = self._old_validate_ssh

    def test_running_install_hosts(self):
        """
        Test packstack.installer.run_setup.main

        This test effectivly runs all of the python code ran by
        packstack --install-hosts=127.0.0.1 --os-swift-install=y

        It is a fairly wide net but boost code coverage of the packstack
        python code to about 85%, more finer grained tests should also be
        Added to target speficic test cases.

        Popen is replaced in PackstackTestCaseMixin so no actual commands get
        run on the host running the unit tests
        """

        subprocess.Popen = FakePopen
        FakePopen.register('cat /etc/resolv.conf | grep nameserver',
                           stdout='nameserver 127.0.0.1')

        # required by packstack.plugins.serverprep_949.mangage_rdo
        FakePopen.register("rpm -q rdo-release "
                           "--qf='%{version}-%{release}.%{arch}\n'",
                           stdout='icehouse-2.noarch\n')
        FakePopen.register_as_script('yum-config-manager --enable '
                                     'openstack-icehouse',
                                     stdout='[openstack-icehouse]\nenabled=1')

        FakePopen.register_as_script(
            'facter -p',
            stdout='operatingsystem => Fedora\noperatingsystemmajrelease => 21'
        )

        # required by packstack.plugins.nova_300.gather_host_keys
        FakePopen.register('ssh-keyscan 127.0.0.1',
                           stdout='127.0.0.1 ssh-rsa hostkey-data')

        # create a dummy public key
        dummy_public_key = os.path.join(self.tempdir, 'id_rsa.pub')
        makefile(dummy_public_key, 'ssh-rsa AAAAblablabla')

        # create dummy keys for live migration mechanism
        makefile(os.path.join(basedefs.VAR_DIR, 'nova_migration_key'),
                 '-----BEGIN RSA PRIVATE KEY-----\n'
                 'keydata\n'
                 '-----END RSA PRIVATE KEY-----\n')
        makefile(os.path.join(basedefs.VAR_DIR, 'nova_migration_key.pub'),
                 'ssh-rsa keydata')

        # Save sys.argv and replace it with the args we want optparse to use
        orig_argv = sys.argv
        sys.argv = ['packstack', '--debug',
                    '--ssh-public-key=%s' % dummy_public_key,
                    '--install-hosts=127.0.0.1', '--os-swift-install=y',
                    '--ssl-cacert-selfsign=y', '--ssl-cert-dir=%s' %
                    os.path.expanduser('~/')]

        # There is no puppet logfile to validate, so replace
        # ospluginutils.validate_puppet_logfile with a mock function
        orig_validate_logfile = puppet.validate_logfile
        puppet.validate_logfile = lambda a: None
        puppet.scan_logfile = lambda a: []

        # mock distro.linux_distribution, it's does subprocess.check_output
        # lsb_release -a
        distro.linux_distribution = lambda: "CentOS"

        # If there is a error in a plugin sys.exit() gets called, this masks
        # the actual error that should be reported, so we replace it to
        # raise Exception, packstack logging gives a more infomrative error
        def raise_(ex):
            raise ex
        orig_sys_exit = sys.exit
        sys.exit = lambda a: raise_(Exception('Error during install-hosts'))

        try:
            run_setup.main()
        finally:
            sys.argv = orig_argv
            ospluginutils.validate_puppet_logfile = orig_validate_logfile
            sys.exit = orig_sys_exit
            try:
                shutil.rmtree(basedefs.VAR_DIR)
            except Exception:
                pass
