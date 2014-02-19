#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

from packstack import version


MODULES_DIR = os.environ.get('PACKSTACK_PUPPETDIR',
                             '/usr/share/openstack-puppet/modules')
MODULES_REPO = ('https://github.com/redhat-openstack/'
                'openstack-puppet-modules.git')
MODULES_BRANCH = 'master'


def install_modules(repo, branch, destination):
    basedir = os.path.dirname(destination.rstrip(' /'))
    repodir = os.path.basename(destination)
    # install third-party modules from openstack-puppet-modules repo
    if not os.path.exists(destination):
        os.makedirs(basedir, 0755)

        print 'Cloning %(repo)s to %(destination)s' % locals()
        cmd = ('cd %(basedir)s; git clone %(repo)s %(repodir)s; '
               'cd %(repodir)s; git checkout %(branch)s; '
               'git submodule update --init' % locals())
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode:
            raise RuntimeError('Failed:\n%s' % err)
    # install Packstack module
    packstack_path = os.path.join(destination, 'packstack')
    print 'Copying Packstack module to %(packstack_path)s' % locals()
    source = os.path.join(os.path.dirname(__file__),
                          'packstack/puppet/modules/packstack')
    shutil.rmtree(packstack_path, ignore_errors=True)
    shutil.copytree(source, packstack_path)


class WithModulesInstall(install):
    def run(self):
        # Code below is from setuptools to make command work exactly
        # as original
        caller = sys._getframe(2)
        caller_module = caller.f_globals.get('__name__', '')
        caller_name = caller.f_code.co_name
        if caller_module != 'distutils.dist' or caller_name != 'run_commands':
            install.run(self)
        else:
            install.do_egg_install(self)

        # install Puppet modules if they don't exist
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            install_modules(MODULES_REPO, MODULES_BRANCH, MODULES_DIR)


class WithModulesDevelop(develop):
    def run(self):
        # super doesn't work here because distutils.cmd.Command
        # is old-style class
        develop.run(self)
        # install Puppet modules if they don't exist
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            install_modules(MODULES_REPO, MODULES_BRANCH, MODULES_DIR)


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    cmdclass={'install': WithModulesInstall, 'develop': WithModulesDevelop},

    name="packstack",
    version=version.version_string(),
    author="Derek Higgins",
    author_email="derekh@redhat.com",
    description=("A utility to install openstack"),
    license="ASL 2.0",
    keywords="openstack",
    url="https://github.com/stackforge/packstack",
    packages=find_packages('.'),
    include_package_data=True,
    long_description=read('README'),
    zip_safe=False,
    install_requires=['netaddr'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    scripts=["bin/packstack"],
)
