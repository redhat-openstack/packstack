#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import subprocess

from setuptools import setup
from setuptools import find_packages
from setuptools import Command

from packstack import version


MODULES_DIR = os.environ.get('PACKSTACK_PUPPETDIR',
                             '/usr/share/openstack-puppet/modules')
MODULES_REPO = ('https://github.com/redhat-openstack/'
                'openstack-puppet-modules.git')
MODULES_BRANCH = 'master-patches'


class InstallModulesCommand(Command):
    description = 'install Puppet modules required to run Packstack'
    user_options = [
        ('destination=', None, 'Directory where to install modules'),
        ('branch=', None, 'Branch which should be used'),
    ]

    def initialize_options(self):
        self.destination = None
        self.branch = None
        self.repo = MODULES_REPO

    def finalize_options(self):
        self.destination = self.destination or MODULES_DIR
        self.branch = self.branch or MODULES_BRANCH

    def run(self):
        destination = self.destination
        basedir = os.path.dirname(self.destination.rstrip(' /'))
        repodir = os.path.basename(self.destination.rstrip(' /'))
        repo = self.repo
        branch = self.branch
        # install third-party modules from openstack-puppet-modules repo
        if not os.path.exists(self.destination):
            try:
                os.makedirs(basedir, 0o755)
            except OSError:
                # base directory exists
                pass
            print('Cloning %(repo)s to %(destination)s' % locals())
            cmd = ('cd %(basedir)s; git clone %(repo)s %(repodir)s; '
                   'cd %(repodir)s; git checkout %(branch)s; ' % locals())
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode:
                raise RuntimeError('Failed:\n%s' % err)
        # install Packstack modules
        module_source = os.path.join(os.path.dirname(__file__),
                                     'packstack/puppet/modules')
        for module in os.listdir(module_source):
            source = os.path.join(module_source, module)
            if not os.path.isdir(source):
                continue

            dest = os.path.join(self.destination, module)
            print('Copying module %(module)s to %(dest)s' % locals())
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(source, dest)


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="packstack",
    version=version.version_string(),
    author="Derek Higgins",
    author_email="derekh@redhat.com",
    description=("A utility to install OpenStack"),
    license="ASL 2.0",
    keywords="openstack",
    url="https://github.com/stackforge/packstack",
    packages=find_packages('.') + ['docs'],
    package_data={'docs': ['docs/packstack.rst']},
    include_package_data=True,
    long_description=read('README.md'),
    zip_safe=False,
    install_requires=['netaddr', 'pyOpenSSL', 'PyYAML', 'docutils'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    scripts=["bin/packstack"],
    cmdclass={'install_puppet_modules': InstallModulesCommand}
)
